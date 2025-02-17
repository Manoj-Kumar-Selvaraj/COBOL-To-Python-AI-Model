import requests
import os

# Your Hugging Face API token
HF_TOKEN = os.getenv("HF_TOKEN")

# Model endpoint (Mistral)
MODEL = "mistralai/Mistral-7B-Instruct-v0.3"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL}"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# Function to read the COBOL raw index text file and convert it into a list
def read_cobol_index(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.readlines()
        return [line.strip() for line in content if line.strip()]
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return []

# Convert the file content into a list
file_path = "COBOL_RAW_INDEX.txt"
cobol_index_list = read_cobol_index(file_path)

# Example output to check the list content
# print(cobol_index_list)

# Function to save the list to a file
def save_list_to_file(data_list, output_file):
    try:
        with open(output_file, 'w') as file:
            # Write the list directly to the file
            # for item in data_list:
            file.write(f"COBOL_LIST = {data_list}\n")
        print(f"Data successfully saved to {output_file}")
    except Exception as e:
        print(f"Error saving data to {output_file}: {e}")

# Save the list to a file
output_file = "COBOL_INDEX_LIST.py"

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
            save_list_to_file(output_data_list[2], output_file)
            # print("Processed List:")
            # print(output_data_list[2])
    except Exception as e:
        print("Failed to parse response:", e)

# Create the prompt with the COBOL index list
prompt = f"""
The following is a list of COBOL index concepts and phrases:

{cobol_index_list}

Please return this data just as a list.
"""

# Query the model with the prompt
query_model(prompt)
