from PYTHON_INDEX_LIST import PYTHON_LIST
from COBOL_INDEX_LIST import COBOL_LIST
import requests
import os
import json

# Your Hugging Face API token
HF_TOKEN = os.getenv("HF_TOKEN")

# Model endpoint (Mistral)
MODEL = "mistralai/Mistral-7B-Instruct-v0.3"

# MODEL = "Salesforce/codet5-base"

API_URL = f"https://api-inference.huggingface.co/models/{MODEL}"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# Function to save the list to a file
def save_list_to_file(data_list, output_file):
    try:
        mapped_data = [item.strip().rstrip(",") for item in data_list]
        
        # Convert JSON string to Python list of dictionaries
        mapped_data.pop()
        # Convert list to a Python dictionary format
        json_string = f"[{', '.join(mapped_data)}]"

        # Convert JSON string to a Python list of dictionaries
        dict_list = json.loads(json_string)    
        with open(output_file, 'w') as file:
            # Write the list directly to the file
            # for item in data_list:
            file.write(f"PYTHON_COBOL_MAPPING = {dict_list}\n")
        print(f"Data successfully saved to {output_file}")
    except Exception as e:
        print(f"Error saving data to {output_file}: {e}")

# Save the list to a file
output_file = "PYTHON_COBOL.py"
# Function to query the model with the list content
def query_model(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {
            "temperature": 0.7,
        }
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    
    try:
        result = response.json()
        if isinstance(result, dict) and "error" in result:
            print("Error:", result["error"])
        else:
            # Clean the output, making sure it's just a list
            # print("This is Result")
            # print(result)
            output_data = result[0]["generated_text"].strip()
            output_data_list = output_data.split('\n')
            save_list_to_file(output_data_list[19:], output_file)
            print("Processed List:")
            # print(output_data_list[19:])
    except Exception as e:
        print("Failed to parse response:", e)

# Create the prompt with the COBOL index list
prompt = f"""
You are an expert in converting legacy COBOL code to Python. I have two lists below:

COBOL Concepts (COBOL_LIST):
{COBOL_LIST}

Python Concepts (PYTHON_LIST):
{PYTHON_LIST}

For each COBOL concept in COBOL_LIST, please map it to the best corresponding Python concept(PYTHON_LIST) based on the lists provided. If No Appropriate matches found for cobol in python data, mention NOT FOUND. Return the mapping as a JSON list where each element is an object with two keys: "cobol_concept" and "python_concept". Also the last numerics of each item in the lists are page numbers of the documentation. Return page numbers in both the values.

For example:
[
    {{"cobol_concept": "DISPLAY phrase", "python_concept": "print() function"}},
    {{"cobol_concept": "MOVE statement", "python_concept": "assignment using '='"}} 
]

Please return only the JSON list in your response with no additional text.
"""

# Query the model with the prompt
query_model(prompt)
