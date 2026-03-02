import json
import optparse
import os
import sys
import logging
import concurrent.futures
from io import BytesIO

import requests
from PIL import Image
from tqdm import tqdm


logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(module)s %(filename)s:%(lineno)s - %(message)s',
                    encoding='utf-8', level=logging.DEBUG)

def get_image_extension(url, response):
    try:
        content_type = response.headers.get("Content-Type")
        if content_type and content_type.startswith("image/"):
            # Map common MIME types to file extensions
            mime_to_extension = {
                "image/jpeg": "jpg",
                "image/png": "png",
                "image/gif": "gif",
                "image/bmp": "bmp",
                "image/webp": "webp",
                "image/tiff": "tiff",
                "image/x-icon": "ico",
            }
            return mime_to_extension.get(content_type, None)
        else:
            return None
    except requests.RequestException as e:
        logger.error(f"Failed to check URL {url}: {e}")
        return None



def check_cache_images(input_data, output_data_path):
    with open(output_data_path, "r") as output_file:
        output_data = json.load(output_file)
    missing_data = []
    completed_ids = []
    for obj in output_data:
        completed_ids.append(obj["data_id"])
    for obj in input_data:
        if obj["data_id"] not in completed_ids:
            missing_data.append(obj)
    return missing_data

def download_image(image_obj, image_save_dir):
    url = image_obj["original"]
    image_id = image_obj["data_id"]

    try:
        response = requests.get(url, timeout=(5, 10))
        response.raise_for_status()
        extension = get_image_extension(url, response)
        if extension is None:
            return {"url": url, "status": "failed"}

        new_directory = os.path.join(image_save_dir, "images")
        os.makedirs(new_directory, exist_ok=True)
        image_path = os.path.join(new_directory, image_id + "." + extension)

        # image_path = image_save_dir + "/" + image_id + "." + extension

        image_obj["image_path"] = image_path
        img = Image.open(BytesIO(response.content))
        if img.mode != "RGB":
            img = img.convert("RGB")
        img.save(image_path)
        logging.info(f"Downloaded {url}")
        return {"url": url, "name": image_path, "status": "success"}
    except Exception as e:
        logging.error(f"Failed to download {url}: {e}")
        return {"url": url, "status": "failed", "error": str(e)}


def download_images_in_parallel(image_objects, image_save_dir, max_workers=5):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(download_image, image_obj, image_save_dir)
            for image_obj in image_objects
        ]
        for future in concurrent.futures.as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                logging.error(f"Error in downloading {e}")
    return results


def download_images_and_write_dataset(input_file, output_dir, max_workers):
    location_name = os.path.abspath(input_file).split('/')[-3]
    filename = os.path.basename(input_file)
    # print(location_name)

    with open(input_file, 'r') as f:
        input_data = json.load(f)
    # create output directories for location
    output_dir = os.path.join(output_dir, location_name)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    data = json.load(open(input_file, 'r'))
    output_dataset_path = os.path.join(output_dir, filename)
    # missing_data = None
    if os.path.isfile(output_dataset_path):
        data = check_cache_images(data, output_dataset_path)
        logger.info(f"Already downloaded: {len(input_data) - len(data)}")
    results = download_images_in_parallel(
        data, output_dir, max_workers=max_workers
    )

    downloaded = {}
    for result in results:
        if result["status"] == "success":
            downloaded[result["url"]] = result["name"]
        # [{result["url"]: result["name"]} for result in results ]
    os.makedirs(os.path.dirname(output_dataset_path), exist_ok=True)
    downloaded_data = []
    for item in input_data:
        if item["original"] in downloaded:
            item["image_path"] = downloaded[item["original"]]
            if not os.path.exists(item["image_path"]):
                logging.info(f"{item['image_path']} does not exist..")
                continue
            downloaded_data.append(item)
    logger.info(f"Total number of images: {len(input_data)}")
    logger.info(f"Number of images to be downloaded: {len(data)}")
    logging.info(f"Number of image downloaded: {len(downloaded_data)}")
    with open(output_dataset_path, 'w') as f:
        json.dump(downloaded_data, f)
    logging.info(f"Saved results to {output_dataset_path}")



if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option('-i', '--input_file', action="store", dest="input_file", default=None, type="string",
                      help='input json dataset file')
    parser.add_option('-o', '--output_dir', action="store", dest="output_dir", default=None, type="string",
                      help="output file path for writing images and final dataset")
    parser.add_option(
        '-w', "--max_workers", type=int, default=5, help="Maximum number of workers"
    )

    options, args = parser.parse_args()
    input_file = options.input_file
    output_dir = options.output_dir
    max_workers = options.max_workers
    if input_file is None:
        logger.error('Input file is required!')
        sys.exit(1)
    if not input_file.endswith(".json"):
        logger.error('Input file should be a json file!')
        sys.exit(1)
    if output_dir is None:
        logger.error('Output directory is required!')
        sys.exit(1)
    download_images_and_write_dataset(input_file, output_dir, max_workers)