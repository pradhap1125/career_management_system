from flask import jsonify
import faiss
from career_management_system.resume_search import load_data, model, filenames


def process_pdf(file):
    resume_dir = "/Users/dheerajkandikattu/Documents/DataBaseProjectPython"
    file.save(resume_dir+file.filename)
    texts=load_data(resume_dir+file.filename)
    for text in texts:
        filenames.append(file.filename)
    index = faiss.read_index("resume_index.faiss")
    embeddings = model.encode(texts, convert_to_numpy=True)
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    faiss.write_index(index, "resume_index.faiss")
    return jsonify(message="File uploaded!")