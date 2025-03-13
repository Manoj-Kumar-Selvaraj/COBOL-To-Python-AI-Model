import fitz  # PyMuPDF for reading PDFs
import openai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Set your OpenAI API Key
openai.api_key = "OPENAI_API_KEY"

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text

# Extract COBOL and Python documentation
cobol_text = extract_text_from_pdf("cobol_doc.pdf")
python_text = extract_text_from_pdf("python_doc.pdf")

# Split text into sections (Assuming each section starts with a keyword)
cobol_sections = cobol_text.split("\n")
python_sections = python_text.split("\n")

# Generate embeddings for text sections
def get_embedding(text):
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return np.array(response["data"][0]["embedding"])

# Create embeddings for COBOL and Python sections
cobol_embeddings = {section: get_embedding(section) for section in cobol_sections if section.strip()}
python_embeddings = {section: get_embedding(section) for section in python_sections if section.strip()}

# Function to find best Python match for a given COBOL query
def find_best_python_match(cobol_query):
    query_embedding = get_embedding(cobol_query)
    best_match = None
    best_score = -1

    for python_text, python_emb in python_embeddings.items():
        similarity = cosine_similarity([query_embedding], [python_emb])[0][0]
        if similarity > best_score:
            best_match = python_text
            best_score = similarity

    return best_match, best_score

# Example Usage
cobol_query = "LENGTH OF"  # Test with COBOL term
best_python_match, score = find_best_python_match(cobol_query)

print(f"COBOL Query: {cobol_query}")
print(f"Best Python Match: {best_python_match} (Score: {score})")
