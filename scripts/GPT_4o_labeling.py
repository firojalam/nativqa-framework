import os
import pandas as pd
from tqdm import tqdm
import requests
import json
import time
import copy
from dotenv import load_dotenv
import argparse

def load_env_azure(env_path):
    load_dotenv(dotenv_path=env_path, override=True)
    deployment_name = os.environ['AZURE_ENGINE_NAME']
    openai_api_base = os.environ['AZURE_API_URL']
    openai_api_key = os.environ['AZURE_API_KEY']
    openai_api_version = os.environ['AZURE_API_VERSION']
    api_url = f"{openai_api_base}/openai/deployments/{deployment_name}/chat/completions?api-version={openai_api_version}"
    headers = {"api-key": openai_api_key}
    return api_url, headers

def load_env(env_path):
    load_dotenv(dotenv_path=env_path, override=True)    
    openai_api_base = os.environ['OPENAI_API_BASE']
    openai_api_key = os.environ['OPENAI_API_KEY']        
    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {openai_api_key}"
    }
    return openai_api_base, headers

def generate_azure(api_url, headers, developer_prompt, user_prompt):
    json_data = {
        "messages": [
        {
            "role": "system",
            "content": developer_prompt
        },            
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt
                    }
                ]
            }
        ],
        "temperature": 0.5,
        "top_p": 0.95,
        "max_tokens": 2000,
        "response_format": {
            "type": "json_object"
        },
    }
    response = requests.post(api_url, headers=headers, json=json_data)
    return response

def generate_openai(headers, developer_prompt, prompt):
    payload = {
        "model": "gpt-4o-2024-11-20",
        "messages": [
            {
                "role": "developer",
                "content": developer_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                ]
            }
        ],
        "max_tokens": 1000,
        "response_format": {"type": "json_object"},
        "temperature": 0.0
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)    
    return response

def deep_copy_dict(original_dict):
    """Create a deep copy of a dictionary"""
    return copy.deepcopy(original_dict)

def process_data(api_url,headers, dataset, op_dir_save, location):
    for index in tqdm(range(len(dataset))):
        data = dataset.iloc[index].to_dict()
        data_obj = deep_copy_dict(data)        
        file_id = data["data_id"]
        
        save_file_name = os.path.join(op_dir_save, file_id + ".json")
        
        del data['input_query']
        del data['category']
        del data['data_id']
        del data['is_reliable']
        del data['question_type']

        developer_prompt = """
        You are an advanced NLP annotation assistant specializing in evaluating Arabic questions and answers. Your role is to classify questions, assess answers, and refine them for conciseness and accuracy.

        Follow the structured guidelines for classification:
        - **Step 1: Classify the question as 'Good' or 'Bad'** based on predefined definitions.
        - **Step 2: Evaluate and refine the answer**, ensuring it is concise and factually correct.
        - **Step 3: Determine if the question-answer pair is relevant to the specified location: {location}.**
        - **Step 4: Based on the question identify its category such as nimal, Business, Cloth, Education, Events, Food & Drinks, General, Geography, Immigration Related, Language, Literature, Names & Persons, Plants, Religion, Sports & Games, Tradition, Travel, Weather**
            
        Your response should strictly follow the required JSON format.
        """

        user_prompt = f"""
        ### **Annotation Task**
        You are an expert Arabic NLP annotator. Your task is to evaluate and refine a question-answer pair based on the following steps:

        ### **Step 1: Categorize the Question as 'Good' or 'Bad'**
        - **Good Question:** A fact-seeking question that can be answered with:
        - A **name** of an entity (person, place, thing, etc.).
        - An **explanation**.
        - A **number**.
        - **Bad Question:** Any question that does not meet the above criteria.

        **Action:**  
        - If 'Bad,' return `"Bad"` and provide a reason.
        - If 'Good,' return `"Good"` and proceed to step 2.

        ### **Step 2: Evaluate and Edit the Answer**
        - **Answer Evaluation:**  
        - **Correct:** Fully and accurately answers the question.  
        - **Incorrect:** Does not answer the question or contains false information.  
        - **Partially Correct:** Provides some relevant information but is incomplete.  
        - **Answer Refinement:**  
        - If correct but **too long, vague, or redundant**, rewrite it to be **concise and precise**.

        ### **Step 3: Determine Location Relevance for location: {location}**
        - **Yes:** The question explicitly refers to the specified location.
        - **No:** The question is about a different location.
        - **Maybe:** The question is general and could apply to multiple locations.
        - **Unsure:** It is difficult to determine whether the question is location-specific.

        ### **Step 4: Identify the Question Category**
        
        ### **Input Data:**
        ```json
        {json.dumps(data, ensure_ascii=False, indent=4)}
        ```

        ### **Your Response in JSON format:**
        {{
        "question_quality": "Good" or "Bad",
        "question_feedback": "Explain why the question is Good or Bad.",
        "answer_evaluation": "Correct" or "Incorrect" or "Partially Correct",
        "answer_feedback": "Explain whether the answer fully addresses the question.",
        "corrected_answer": "Provide a concise, precise answer if needed, otherwise leave empty.",
        "location_relevance": "Yes" or "No" or "Maybe" or "Unsure",
        "location_feedback": "Explain why the question is relevant or not to the specified location."
        "question_category": "Animal" or "Business" or "Cloth" or "Education" or "Events" or "Food & Drinks" or "General" or "Geography" or "
        }}

        """
        
        if os.path.exists(save_file_name):
            continue

        try:    
            response = generate_azure(api_url, headers, developer_prompt, user_prompt)
            data_obj["response"] = response.json()    

            # save response to disk as a JSON file
            with open(save_file_name, 'w') as json_file:
                json.dump(data_obj, json_file, ensure_ascii=False, indent=4)

            st_time = time.time()
        except Exception as e:
            print(file_id)
            print(e)
            time.sleep(2)    

def main():
    parser = argparse.ArgumentParser(description="Process dataset with GPT-4o")
    parser.add_argument("-i",'--input_file', type=str, required=True, help='Path to the input JSON file')
    parser.add_argument("-e",'--env_path', type=str, required=True, help='Path to the .env file')
    parser.add_argument("-o", "--output_dir", type=str, required=True, help="Output directory for json files")
    parser.add_argument("-l",'--location', type=str, required=True, help='Location for relevance determination')
    args = parser.parse_args()

    input_file = args.input_file
    env_path = args.env_path
    location = args.location
    output_dir = args.output_dir

    dir_path = os.path.abspath(os.path.dirname(output_dir))
    #openai_api_base, headers = load_env(env_path)
    api_url, headers = load_env_azure(env_path)
    

    dataset = pd.read_json(input_file)
    print('Number of samples in the dataset: ', len(dataset))
    dataset.head()

    parent_dir = os.path.dirname(input_file)
    parent_dir_name = os.path.basename(parent_dir)
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    op_dir_save = os.path.join(dir_path, base_name)
    os.makedirs(op_dir_save, exist_ok=True)

    process_data(api_url,headers, dataset, op_dir_save, location)

if __name__ == "__main__":
    main()