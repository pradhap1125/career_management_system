from flask import Flask, request, jsonify
from psycopg_pool import ConnectionPool

from career_management_system import dbService
from career_management_system.pdf_processor import process_pdf
from career_management_system.resume_search import search_resume

app = Flask(__name__)

@app.route("/api/applicant", methods=["GET"])
def get_applicants():
    return dbService.get_applicants()

@app.route("/api/applicant/<int:user_id>", methods=["GET"])
def get_applicants_id(user_id):
    return dbService.get_applicants(user_id)


@app.route("/api/applicant", methods=["POST"])
def create_applicants():
    data = request.get_json()
    return dbService.create_applicants(data)

@app.route("/api/applicant/<int:user_id>", methods=["PUT"])
def update_applicant(user_id):
    data = request.get_json()
    return dbService.update_applicant(user_id, data)

@app.route("/api/applicant/<int:user_id>", methods=["DELETE"])
def delete_applicant(user_id):
    return dbService.delete_applicant(user_id)

@app.route('/app/uploadresume', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are allowed'}), 400

    return process_pdf(file)

@app.route('/app/searchresume', methods=['POST'])
def search():
    data = request.get_json()
    return search_resume(data['keywords'])

if __name__ == "__main__":
    app.run(debug=True)