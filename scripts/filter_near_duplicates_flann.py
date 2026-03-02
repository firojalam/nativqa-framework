import argparse
import datetime
import json
import logging
import os
import pickle
import time
import warnings

import numpy as np
import torch
import torchvision.transforms as transforms
from PIL import Image
from pyflann import FLANN
from sklearn.neighbors import NearestNeighbors
from torch import nn
from torchvision.models import resnet18, ResNet18_Weights
from tqdm import tqdm


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Constants
IMG_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".ppm", ".bmp", ".pgm", ".webp"}


# Check if a file is an image
def is_image_file(filename):
    return filename.lower().endswith(tuple(IMG_EXTENSIONS))


# Ensure directory exists
def check_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def load_model():
    """
    Load a pre-trained ResNet-18 model and remove the final classification layer.

    Returns:
        torch.nn.Module: The feature extraction model.
    """
    # Load pre-trained ResNet-18
    model = resnet18(weights=ResNet18_Weights.DEFAULT)

    # Remove the classification layer (fully connected layer)
    model = nn.Sequential(*list(model.children())[:-1])

    # Enable multi-GPU support
    model = torch.nn.DataParallel(model).cuda()

    # Set model to evaluation mode (important for feature extraction)
    model.eval()

    return model


def read_image_list_jsonl(file_path):
    """
    Reads a JSONL file and returns a list of dictionaries.

    Args:
        file_path (str): Path to the JSONL file.

    Returns:
        list: A list of dictionaries containing the JSONL data.
    """
    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in tqdm(f, desc="Reading entries from file"):
            try:
                json_object = json.loads(line.strip())

                image_path = json_object["image_path"]
                if not os.path.exists(image_path):
                    continue

                file_extension = os.path.splitext(image_path)[-1].lower()
                if file_extension == ".webp":
                    output_file = os.path.splitext(image_path)[0] + ".jpg"
                    image = Image.open(image_path)
                    image.convert("RGB").save(output_file, "JPEG")
                    json_object["image_path"] = output_file
                data.append(json_object)
            except Exception as e:
                logging.error(f"Error decoding JSON on line: {line.strip()}\n{e}")
    logging.info(f"Loaded {len(data)} images.")
    return data


def extract_features(
    model, image_objects, output_file_name, fc_dim=1024, calculate_img_scores=True
):
    """
    Extracts image features using a pre-trained model.

    Args:
        model (torch.nn.Module): The feature extraction model.
        images (list): List of image metadata dictionaries with "path" key.
        output_file_name (str): File path for saving extracted features.
        calculate_img_scores (bool): Whether to compute features or load from file.
        fc_dim (int): Feature dimension.

    Returns:
        tuple: (features, filtered_images), where features is a NumPy array of extracted features
               and filtered_images contains successfully processed image metadata.
    """
    # Define image preprocessing pipeline
    transform = transforms.Compose(
        [
            transforms.Resize((256, 256)),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    )

    # Prepare output paths
    output_dir = os.path.dirname(output_file_name)
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(output_file_name))[0]

    feature_file = os.path.join(output_dir, f"{base_name}.npy")
    img_info_file = os.path.join(output_dir, f"{base_name}.pkl")

    if not calculate_img_scores:
        # Load features from disk if already computed
        features = np.load(feature_file)
        with open(img_info_file, "rb") as f:
            filtered_image_objects = pickle.load(f)
        print(f"Loaded features from {feature_file}, shape: {features.shape}")
        return features, filtered_image_objects

    # Initialize feature storage
    features = np.empty((len(image_objects), fc_dim), dtype=np.float32)
    filtered_image_objects = []

    # Set model to evaluation mode
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    with torch.no_grad():
        for img_idx, img_object in enumerate(
            tqdm(image_objects, desc="Extracting features")
        ):
            img_name = img_object.get("image_path")
            try:
                img = Image.open(img_name).convert("RGB")
                input_tensor = transform(img).unsqueeze(0).to(device)

                # Forward pass to get features
                features[img_idx] = model(input_tensor).squeeze().cpu().numpy()
                filtered_image_objects.append(img_object)
            except Exception as e:
                logging.error(f"Error processing {img_object['image_path']}: {e}")
    # Save features and metadata
    np.save(feature_file, features)

    print(
        f"Saved {len(filtered_image_objects)} extracted features to {feature_file}, shape: {features.shape}"
    )
    return features, filtered_image_objects


def compute_duplicate_flann(features, output_file_name, threshold):
    """
    Compute duplicate images using FLANN nearest neighbors search.

    Args:
        features (np.ndarray): Feature matrix where each row corresponds to an image feature vector.
        output_file_name (str): Path to save the duplicate detection results.
        threshold (float): Radius for nearest neighbor search.

    Returns:
        tuple: (nbr_distances, nbr_indices) containing neighbor distances and indices.
    """
    nearest_neighbor_start_time = time.time()
    flann = FLANN()
    flann.build_index(features, algorithm="kdtree", trees=8, checks=64)
    nbr_distances = np.empty(features.shape[0], dtype=object)
    nbr_indices = np.empty(features.shape[0], dtype=object)

    for i in tqdm(range(features.shape[0])):
        indices, dists = flann.nn_radius(features[i], threshold)
        nbr_indices[i] = np.sort(indices)
        ind = np.argsort(indices)
        nbr_distances[i] = [dists[j] for j in ind]

    dir_name = os.path.dirname(output_file_name)
    base_name = os.path.basename(output_file_name)
    base_name = os.path.splitext(base_name)[0]
    out_all_neighbor_info_file = (
        dir_name + "/" + base_name + "_neighbor_info_th_" + str(threshold) + ".pkl"
    )

    logging.info(
        "Nearest neighbor calculation time: %.3f seconds",
        (time.time() - nearest_neighbor_start_time),
    )
    with open(out_all_neighbor_info_file, "wb") as f:
        pickle.dump((nbr_distances, nbr_indices), f, protocol=pickle.HIGHEST_PROTOCOL)

    seen_indices = set()
    nonduplicate_indices = set()
    duplicate_indices = dict()
    for i in range(nbr_indices.size):
        if i in seen_indices:
            continue
        nonduplicate_indices.add(int(i))
        dups = []
        for j in nbr_indices[i]:
            seen_indices.add(int(j))
            dups.append(int(j))
        duplicate_indices[i] = dups

    return nbr_distances, nbr_indices, nonduplicate_indices, duplicate_indices


def make_serializable(obj):
    if isinstance(obj, np.float32):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")


def write_nn_results(file_name, nbr_indices, nbr_distances, image_objects):
    dir_name = os.path.dirname(file_name)
    base_name, _ = os.path.splitext(os.path.basename(file_name))
    out_file_name = os.path.join(dir_name, f"{base_name}_nn.jsonl")

    logging.info(f"Number of nearest neighbor indices: {len(nbr_indices)}")

    with open(out_file_name, "w") as out_file:
        for index, image_obj in enumerate(image_objects):
            image_path = image_obj["image_path"]

            if index >= len(nbr_indices):  # Skip if index is out of range
                continue

            neighbors = [image_objects[j] for j in nbr_indices[index]]
            distances = nbr_distances[index]

            data = {
                neighbor["image_path"]: dist
                for neighbor, dist in zip(neighbors, distances)
                if not (dist == 0.0 and neighbor["image_path"] == image_path)
            }

            if data:
                json_str = json.dumps({image_path: data}, default=make_serializable)
                out_file.write(json_str + "\n")
    logging.info(f"Nearest neighbor results saved to {out_file_name}")


def save_filtered_data(nonduplicate_indices, filtered_image_objects, output_file):
    with open(output_file, "w") as jsonl_file:
        for i in nonduplicate_indices:
            img_object = filtered_image_objects[i]
            jsonl_file.write(json.dumps(img_object, ensure_ascii=False) + "\n")

    logging.info(f"Saved results to {output_file}")


if __name__ == "__main__":
    start_time = datetime.datetime.now()

    parser = argparse.ArgumentParser(description="Process some images.")
    parser.add_argument(
        "-i",
        "--input_file",
        type=str,
        required=True,
        help="Input file containing image paths",
    )
    parser.add_argument(
        "-o",
        "--output_file",
        type=str,
        required=True,
        help="Output file to save results",
    )
    parser.add_argument(
        "-t",
        "--threshold",
        type=float,
        default=1.5,
        help="Threshold for duplicate detection",
    )
    parser.add_argument(
        "-f",
        "--fc_dim",
        type=int,
        default=512,
        help="Feture dimension",
    )
    args = parser.parse_args()

    logging.info(f"Input arguments: {args}")

    images_objects = read_image_list_jsonl(args.input_file)

    model = load_model()
    features, filtered_image_objects = extract_features(
        model,
        images_objects,
        args.output_file,
        fc_dim=args.fc_dim,
        calculate_img_scores=True,
    )

    (
        nbr_distances,
        nbr_indices,
        nonduplicate_indices,
        duplicate_indices,
    ) = compute_duplicate_flann(features, args.output_file, args.threshold)
    write_nn_results(
        args.output_file, nbr_indices, nbr_distances, filtered_image_objects
    )
    save_filtered_data(nonduplicate_indices, filtered_image_objects, args.output_file)

    # generate_nn_html(file_name, nbr_indices, nbr_distances, images_objects, images_objects, source,threshold)

    logging.info(f"Original number of images: {len(images_objects)}")
    logging.info(f"Number of images after filtering: {len(nonduplicate_indices)}")
    logging.info(f"Total execution time: {datetime.datetime.now() - start_time}")
