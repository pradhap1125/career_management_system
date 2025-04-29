import os
from pdfminer.high_level import extract_text
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss

#model = SentenceTransformer('all-MiniLM-L6-v2')
#model = SentenceTransformer('C:\\Users\\pradh\\fine_tuned_sentence_transformer\\')
model = SentenceTransformer('sentence-transformers/multi-qa-mpnet-base-dot-v1')
filenames = []

def extract_text_from_pdf(pdf_path):
    text = extract_text(pdf_path)
    return text

def load_data(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=16, chunk_overlap=0)
    texts = text_splitter.split_text(text)
    return texts

def create_faiss_index(embeddings):
    d = embeddings.shape[1]
    index = faiss.IndexFlatIP(d)
    index.add(np.array(embeddings))
    return index

def search_faiss_index(index, query_embedding, filenames, k=10):
    threshold = 0.7
    distances, indices = index.search(np.array(query_embedding), k)
    filtered_results = [
        filenames[indices[0][i]]
        for i in range(len(indices[0]))
        if distances[0][i] >= threshold and indices[0][i] < len(filenames)
    ]

    return filtered_results

# Main Script
def initial_vector_load():
    resume_dir = "/Users/dheerajkandikattu/Documents/DataBaseProjectPython"
    all_texts = []
    global filenames
#    model.fit
    for file in os.listdir(resume_dir):
        if file.endswith(".pdf"):
            file_path = os.path.join(resume_dir, file)
            texts = load_data(file_path)
            for text in texts:
                all_texts.append(text)
                filenames.append(file)


    embeddings = model.encode(all_texts, normalize_embeddings=True)
    embeddings = np.array(embeddings).astype('float32')

    if len(embeddings) == 0:
        return
    index = create_faiss_index(embeddings)

    faiss.write_index(index, "resume_index.faiss")

def search_resume(keyword):
    index = faiss.read_index("resume_index.faiss")
    query_embedding = model.encode([keyword], normalize_embeddings=True)
    query_embedding = np.array(query_embedding).astype('float32')
    results = search_faiss_index(index, query_embedding, filenames)

    return list(set(results))

initial_vector_load()