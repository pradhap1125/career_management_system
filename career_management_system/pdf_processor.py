import os

from flask import jsonify
import faiss
import numpy as np
from career_management_system.resume_search import load_data, model, filenames


def process_pdf(file):
    resume_dir = "D:\\resume_test\\"
    file.save(resume_dir+file.filename)
    texts=load_data(resume_dir+file.filename)
    for text in texts:
        filenames.append(file.filename)
    index = faiss.read_index("resume_index.faiss")
    embeddings = model.encode(texts, normalize_embeddings=True)
    embeddings = np.array(embeddings).astype('float32')
    index.add(embeddings)
    faiss.write_index(index, "resume_index.faiss")
    return jsonify(message="File uploaded!")

def delete_pdf(fileName):
    resume_dir = "D:\\resume_test\\"
    file_path = resume_dir + fileName
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify(message="File deleted!")
    else:
        return jsonify(message="File not found!")