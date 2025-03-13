import openai
import os
import json
import re
from PYTHON_INDEX_LIST import PYTHON_INDEX_LIST
from COBOL_INDEX_LIST import COBOL_INDEX_LIST

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY environment variable is not set.")

client = openai.OpenAI()

# Function to save the mapped list to a file
def save_list_to_file(data_list, output_file):
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(f"PYTHON_COBOL_MAPPING = {json.dumps(data_list, indent=4)}\n")
        print(f"✅ Data successfully saved to {output_file}")
    except Exception as e:
        print("❌ Error saving file:", e)

# Function to call OpenAI API
def query_openai(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in mapping COBOL concepts to Python."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )

        # Extract API response
        output_data = response.choices[0].message.content.strip()
        print("📥 Raw API Response:\n", output_data)

        # Remove Markdown formatting
        json_match = re.search(r'```(?:json)?\s*([\s\S]+?)\s*```', output_data)
        if json_match:
            output_data = json_match.group(1).strip()

        # Validate JSON format
        try:
            return json.loads(output_data)
        except json.JSONDecodeError:
            print("❌ Unexpected response format. Could not extract valid JSON.")
            return []
    except Exception as e:
        print("❌ Failed to query OpenAI API:", e)
        return []

# Function to split list into chunks
def split_list(lst, chunk_size):
    """Splits a list into smaller chunks of `chunk_size`."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

# Process list in chunks
def process_cobol_to_python_mapping():
    all_mappings = []

    # Define chunk size (e.g., 20 items per batch)
    chunk_size = 100

    for index, chunk in enumerate(split_list(COBOL_INDEX_LIST, chunk_size)):
        print(f"🚀 Processing chunk {index + 1}/{(len(COBOL_INDEX_LIST) // chunk_size) + 1}")

        prompt = f"""
        You are an expert in converting legacy COBOL code to Python. Your task is to map COBOL concepts to their closest equivalent Python concepts.

        ### COBOL Concepts:
        {chunk}

        ### Python Concepts:
        {PYTHON_INDEX_LIST}

        ### Instructions:
        - For **each** COBOL concept, find the best matching Python concept.
        - If no suitable match is found, set the Python concept as `"NOT FOUND"`.
        - **Do not exclude any COBOL concepts**; ensure every item in the chunk is included in the output.

        ### Output Format:
        Return the result as a **valid JSON array** where:
        - Each object contains `"cobol_concept"` and `"python_concept"` keys.
        - Ensure the JSON is **well-formatted** with no extra text.

        ### Example Output:
        ```json
        [
            {{"cobol_concept": "DISPLAY phrase", "python_concept": "print() function"}},
            {{"cobol_concept": "MOVE statement", "python_concept": "assignment using '='"}},
            {{"cobol_concept": "UNMATCHED_CONCEPT", "python_concept": "NOT FOUND"}}
        ]
        ```
        """

        chunk_mapping = query_openai(prompt)
        all_mappings.extend(chunk_mapping)

    # Save final combined result
    save_list_to_file(all_mappings, "PYTHON_COBOL.py")
    print("✅ All COBOL concepts processed and saved!")

if __name__ == "__main__":
    process_cobol_to_python_mapping()
