import os
from pdfminer.high_level import extract_text
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss

# model = SentenceTransformer('all-MiniLM-L6-v2')
model = SentenceTransformer('C:\\Users\\pradh\\fine_tuned_sentence_transformer\\')
filenames = []

def extract_text_from_pdf(pdf_path):
    text = extract_text(pdf_path)
    return text

def load_data(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=256, chunk_overlap=0)
    texts = text_splitter.split_text(text)
    return texts

def create_faiss_index(embeddings):
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index

def search_faiss_index(index, query_embedding, filenames, k=2):
    distances, indices = index.search(query_embedding, k)
    return [filenames[i] for i in indices[0]]

# Main Script
def initial_vector_load():
    resume_dir = "D:\\resume_test\\"
    all_texts = []
    global filenames
    model.fit
    for file in os.listdir(resume_dir):
        if file.endswith(".pdf"):
            file_path = os.path.join(resume_dir, file)
            texts = load_data(file_path)
            for text in texts:
                all_texts.append(text)
                filenames.append(file)


    embeddings = model.encode(all_texts, convert_to_numpy=True)
    faiss.normalize_L2(embeddings)

    index = create_faiss_index(embeddings)

    faiss.write_index(index, "resume_index.faiss")

def search_resume(keyword):
    index = faiss.read_index("resume_index.faiss")
    query_embedding = model.encode([keyword], convert_to_numpy=True)
    emb_res = np.array(query_embedding).reshape(1, -1)
    faiss.normalize_L2(emb_res)
    results = search_faiss_index(index, emb_res, filenames)

    return list(set(results))

initial_vector_load()