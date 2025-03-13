import fitz  # PyMuPDF for reading PDFs
import openai
import numpy as np
import os
import importlib.util
from sklearn.metrics.pairwise import cosine_similarity

# Load PYTHON_COBOL_MAPPING from external Python file
MAPPING_FILE = "python_cobol_mapping.py"
spec = importlib.util.spec_from_file_location("mapping_module", MAPPING_FILE)
mapping_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mapping_module)
PYTHON_COBOL_MAPPING = mapping_module.PYTHON_COBOL_MAPPING

# OpenAI API Key (Set your actual key here)
openai.api_key = "OPENAI_API_KEY"

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text

# Load COBOL documentation
COBOL_DOC_PATH = "cobol_doc.pdf"
cobol_doc_text = extract_text_from_pdf(COBOL_DOC_PATH)
cobol_sections = cobol_doc_text.split("\n")

# Generate embeddings for documentation sections
def get_embedding(text):
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return np.array(response["data"][0]["embedding"])

# Store embeddings for COBOL documentation
cobol_embeddings = {section: get_embedding(section) for section in cobol_sections if section.strip()}

# Function to find relevant documentation for COBOL code
def find_relevant_doc(cobol_code):
    query_embedding = get_embedding(cobol_code)
    best_match = None
    best_score = -1
    for section, emb in cobol_embeddings.items():
        similarity = cosine_similarity([query_embedding], [emb])[0][0]
        if similarity > best_score:
            best_match = section
            best_score = similarity
    return best_match if best_score > 0.5 else ""

# Function to convert COBOL to Python
def convert_cobol_to_python(cobol_code):
    # Extract relevant mapping
    mappings = [m for m in PYTHON_COBOL_MAPPING if m["cobol_concept"] in cobol_code]
    prompt = "Convert this COBOL program to Python while following these mappings: \n\n"
    for mapping in mappings:
        prompt += f"COBOL: {mapping['cobol_concept']} -> Python: {mapping['python_concept']}\n"
    
    # Add relevant documentation
    relevant_doc = find_relevant_doc(cobol_code)
    if relevant_doc:
        prompt += f"\nAdditional COBOL Documentation:\n{relevant_doc}\n"
    
    prompt += f"\nCOBOL Code:\n{cobol_code}\n\nPython Equivalent:"  
    
    response = openai.Completion.create(
        model="code-davinci-002",
        prompt=prompt,
        temperature=0.3,
        max_tokens=300
    )
    return response["choices"][0]["text"].strip()

# Process COBOL files and save Python equivalents
COBOL_FOLDER = "COBOL_FILES"
PYTHON_FOLDER = "PYTHON_CONVERSIONS"
os.makedirs(PYTHON_FOLDER, exist_ok=True)

for filename in os.listdir(COBOL_FOLDER):
    if filename.endswith(".cob"):  # Assuming .cob as COBOL file extension
        cobol_path = os.path.join(COBOL_FOLDER, filename)
        with open(cobol_path, "r") as file:
            cobol_code = file.read()
        python_code = convert_cobol_to_python(cobol_code)
        
        python_filename = filename.replace(".cob", ".py")
        python_path = os.path.join(PYTHON_FOLDER, python_filename)
        with open(python_path, "w") as py_file:
            py_file.write(python_code)
        print(f"Converted {filename} -> {python_filename}")
