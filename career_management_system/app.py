from flask import Flask, request, jsonify

from career_management_system import dbService
from career_management_system.dbService import execute_query
from career_management_system.pdf_processor import process_pdf
from career_management_system.resume_search import search_resume
from career_management_system.sql_generation_llm import generate_sql, is_valid_sql
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/api/applicant", methods=["GET"])
def get_applicants():
    return dbService.get_applicants()

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    return dbService.login(data)

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

@app.route('/api/uploadresume', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are allowed'}), 400

    return process_pdf(file)

@app.route('/api/searchresume', methods=['POST'])
def search():
    data = request.get_json()
    return search_resume(data['keywords'])

@app.route('/api/generateData', methods=['POST'])
def generateSql():
    data = request.get_json()
    generated_txt=generate_sql(data['query'])
    generated_txt=generated_txt.replace("sql","").replace("```","")
    if is_valid_sql(generated_txt):
        return execute_query(generated_txt)
    else:
        return generated_txt

@app.route('/api/skillmaster', methods=['GET'])
def skill_master():
    return dbService.skill_master()

@app.route('/api/educationmaster', methods=['GET'])
def education_master():
    return dbService.education_master()

@app.route('/api/companymaster', methods=['GET'])
def company_master():
    return dbService.company_master()

@app.route('/api/certificationmaster', methods=['GET'])
def certification_master():
    return dbService.certification_master()

@app.route('/api/majormaster', methods=['GET'])
def major_master():
    return dbService.major_master()

@app.route('/api/locationmaster', methods=['GET'])
def location_master():
    return dbService.location_master()

@app.route('/api/degreemaster', methods=['GET'])
def degree_master():
    return dbService.degree_master()

if __name__ == "__main__":
    app.run(debug=True)