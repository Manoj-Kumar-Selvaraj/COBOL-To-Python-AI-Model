import openai
import os

# Load OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Function to read the Python raw index text file and convert it into a list
def read_python_index(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.readlines()
        return [line.strip() for line in content if line.strip()]
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return []

# Convert the file content into a list
file_path = "PYTHON_RAW_INDEX.txt"
python_index_list = read_python_index(file_path)

# OpenAI API call function
def query_openai(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI that formats lists."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )

        # Get the content properly
        output_data = response.choices[0].message.content.strip()

        # Remove unwanted text, code blocks, and clean the response
        output_data = output_data.replace("```python", "").replace("```", "").strip()
        output_data_lines = output_data.split("\n")

        # Filter out unwanted lines
        cleaned_list = []
        for line in output_data_lines:
            line = line.strip().strip(",")  # Remove extra spaces and trailing commas
            if line and not line.startswith("Here's") and not line.startswith("[") and not line.startswith("]"):
                cleaned_list.append(line.strip("'").strip('"'))  # Remove extra quotes

        return cleaned_list
    except Exception as e:
        print("Failed to query OpenAI API:", e)
        return []

# Create the prompt with the Python index list
prompt = f"""
The following is a list of Python index concepts and phrases:

{python_index_list}

Please return this data as a clean Python list format, keeping the structure but removing unnecessary numbers. Output only the Python list, nothing else.
"""

# Query OpenAI and process the response
cleaned_python_list = query_openai(prompt)

# Function to save the processed list to a file
def save_list_to_file(data_list, output_file):
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(f"PYTHON_INDEX_LIST = {data_list}\n")
        print(f"Data successfully saved to {output_file}")
    except Exception as e:
        print(f"Error saving data to {output_file}: {e}")

# Save the cleaned list to a file
output_file = "PYTHON_INDEX_LIST.py"
save_list_to_file(cleaned_python_list, output_file)
