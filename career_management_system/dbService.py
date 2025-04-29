import json

import pandas as pd
from flask import jsonify
from psycopg_pool import ConnectionPool

from career_management_system.HashService import hash_password

DB_CONFIG = "dbname=Career_Management_System user=postgres password=Chottu@1125 host=localhost port=5432"
pool = ConnectionPool(conninfo=DB_CONFIG, min_size=1, max_size=10)


def get_applicants(user_id=None):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            if user_id is None:
                cur.execute("SELECT * FROM Applicant_data")
                json_list = []
                applicants = cur.fetchall()
                for a in applicants:
                    education, experience, skills, certifications=get_entities(a[0])
                    json_list.append(

                        {"id": a[0], "first_name": a[1], "last_name": a[2], "email_id": a[3], "phone": a[4],
                         "address": a[5], "location_id": a[6],"resume_name": a[9],
                         "education": [{"id": e[0], "institute_name": e[1], "degree": e[2], "major": e[3],
                                        "start_date": e[4], "end_date": e[5]} for e in education],
                         "experience": [
                             {"id": e[0], "company": e[1], "title": e[2], "start_date": e[3], "end_date": e[4]}
                             for e in experience],
                         "skills": [{"id": s[0], "skill_name": s[1]} for s in skills],
                         "certifications": [{"id": c[0], "certification_name": c[1], "issuing_date": c[2]} for c in
                                            certifications]
                         }
                    )
                return jsonify(json_list)

            else:
                cur.execute("SELECT * FROM Applicant_data WHERE id = %s;", (user_id,))
                a = cur.fetchone()
                education, experience, skills, certifications = get_entities(user_id)
                return jsonify(
                    {"id": a[0], "first_name": a[1], "last_name": a[2], "email_id": a[3], "phone": a[4],
                     "address": a[5], "location_id": a[6],
                     "education": [{"id": e[0], "institute_name": e[1], "degree": e[2], "major": e[3],
                                    "start_date": e[4], "end_date": e[5]} for e in education],
                     "experience": [
                         {"id": e[0], "company": e[1], "title": e[2], "start_date": e[3], "end_date": e[4]}
                         for e in experience],
                     "skills": [{"id": s[0], "skill_name": s[1]} for s in skills],
                     "certifications": [{"id": c[0], "certification_name": c[1], "issuing_date": c[2]} for c in
                                        certifications]
                     }
                )

def get_entities(user_id):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT e.id, u.institute_name, d.name, m.major_name, e.start_date, e.end_date
                FROM Applicant_education e left join university_master u on e.education_id = u.id
                left join degree_master d on e.degree_id = d.id
                left join major_master m on e.major_id = m.id
                WHERE e.applicant_id = %s;
            """, (user_id,))
            education = cur.fetchall()

            cur.execute("""
                SELECT e.id, c.name, e.job_title, e.start_date, e.end_date
                FROM Applicant_experience e
                left join company_master c on e.company_id = c.id
                WHERE e.applicant_id = %s;
            """, (user_id,))
            experience = cur.fetchall()

            cur.execute("""
                SELECT s.id, sm.name
                FROM Applicant_skills s left join skills_master sm on s.skill_id = sm.id
                WHERE s.applicant_id = %s;
            """, (user_id,))
            skills = cur.fetchall()

            cur.execute("""
                SELECT c.id, cm.name, c.given_date
                FROM Applicant_Certification c left join certification_master cm on c.certification_id = cm.id
                WHERE c.applicant_id = %s;
            """, (user_id,))
            certifications = cur.fetchall()

            return education, experience, skills, certifications

def create_applicants(data):
    with pool.connection()  as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO Applicant_data (first_name, last_name, email_id, phone, address, location_id,resume_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;
            """, (data['first_name'], data['last_name'], data['email_id'], data['phone'], data.get('address', None),
                  data['location_id'],data['resume_name']))
            user_id = cur.fetchone()[0]

            for edu in data.get('education', []):
                cur.execute("""
                            INSERT INTO Applicant_education (applicant_id, education_id, degree_id, major_id, start_date, end_date)
                            VALUES (%s, %s, %s, %s, %s, %s);
                        """, (user_id, edu['education_id'], edu['degree_id'], edu['major_id'], edu['start_date'],
                              edu['end_date']))

            for exp in data.get('experience', []):
                cur.execute("""
                            INSERT INTO Applicant_experience (applicant_id, company_id,job_title, start_date, end_date)
                            VALUES (%s, %s, %s, %s,%s);
                        """, (user_id, exp['company_id'],exp['job_title'], exp['start_date'], exp.get('end_date', None)))

            for skill in data.get('skills', []):
                cur.execute("""
                            INSERT INTO Applicant_skills (applicant_id, skill_id)
                            VALUES (%s, %s);
                        """, (user_id, skill['skill_id']))

            for cert in data.get('certifications', []):
                cur.execute("""
                            INSERT INTO Applicant_Certification (applicant_id, certification_id, given_date)
                            VALUES (%s, %s, %s);
                        """, (user_id, cert['certification_id'], cert['given_date']))
            conn.commit()
    return jsonify({"id":user_id})

def update_applicant(user_id,data):
    with pool.connection()  as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE Applicant_data 
                SET first_name = %s, last_name = %s, email_id = %s, phone = %s, address = %s, update_timestamp = CURRENT_TIMESTAMP
                WHERE id = %s RETURNING id
            """, (data["first_name"], data["last_name"], data["email_id"], data["phone"], data.get("address"), user_id))
            updated = cur.fetchone()

            if 'education' in data:
                cur.execute("DELETE FROM Applicant_education WHERE applicant_id = %s;", (user_id,))
                for edu in data['education']:
                    cur.execute("""
                        INSERT INTO Applicant_education (applicant_id, education_id, degree_id, major_id, start_date, end_date)
                        VALUES (%s, %s, %s, %s, %s, %s);
                    """, (user_id, edu['education_id'], edu['degree_id'], edu['major_id'], edu['start_date'],
                          edu['end_date']))

            if 'experience' in data:
                cur.execute("DELETE FROM Applicant_experience WHERE applicant_id = %s;", (user_id,))
                for exp in data['experience']:
                    cur.execute("""
                        INSERT INTO Applicant_experience (applicant_id, company_id,job_title, start_date, end_date)
                        VALUES (%s, %s, %s, %s);
                    """, (user_id, exp['company_id'],exp['job_title'], exp['start_date'], exp.get('end_date', None)))

            if 'skills' in data:
                cur.execute("DELETE FROM Applicant_skills WHERE applicant_id = %s;", (user_id,))
                for skill in data['skills']:
                    cur.execute("""
                        INSERT INTO Applicant_skills (applicant_id, skill_id)
                        VALUES (%s, %s);
                    """, (user_id, skill['skill_id']))

            if 'certifications' in data:
                cur.execute("DELETE FROM Applicant_Certification WHERE applicant_id = %s;", (user_id,))
                for cert in data['certifications']:
                    cur.execute("""
                        INSERT INTO Applicant_Certification (applicant_id, certification_id, given_date)
                        VALUES (%s, %s, %s);
                    """, (user_id, cert['certification_id'], cert['given_date']))
            conn.commit()

    if updated:
        return jsonify({"id":user_id})
    else:
        raise Exception("User not found")

def get_resume_name(user_id):
    with pool.connection()  as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT resume_name
                FROM Applicant_data 
                WHERE id = %s;
            """, (user_id,))
            resume_name = cur.fetchone()
            if resume_name:
                return resume_name[0]
            else:
                raise Exception("User not found")

def delete_applicant(user_id):
    with pool.connection()  as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Applicant_education WHERE applicant_id = %s;", (user_id,))
            cur.execute("DELETE FROM Applicant_experience WHERE applicant_id = %s;", (user_id,))
            cur.execute("DELETE FROM Applicant_skills WHERE applicant_id = %s;", (user_id,))
            cur.execute("DELETE FROM Applicant_Certification WHERE applicant_id = %s;", (user_id,))
            cur.execute("DELETE FROM Applicant_data WHERE id = %s RETURNING id", (user_id,))
            deleted = cur.fetchone()
            conn.commit()
    if deleted:
        return jsonify({"message": f"User {user_id} deleted"})
    else:
        raise Exception("User not found")

def execute_query(query):
    with pool.connection()  as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            data = cur.fetchall()
            columns = [desc[0] for desc in cur.description]  # Extract column names
            df = pd.DataFrame(data, columns=columns)
            return df.to_json(orient='records')

def skill_master():
    with pool.connection()  as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM skills_master")
            skills=cur.fetchall()
            json_list= [{"id": s[0], "name": s[1]} for s in skills]
            return jsonify(json_list)

def location_master():
    with pool.connection()  as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name,state,country FROM location_master")
            location = cur.fetchall()
            json_list = [{"id": s[0], "city": s[1],"state":s[2],"country":s[3]} for s in location]
            return jsonify(json_list)

def education_master():
    with pool.connection()  as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, institute_name FROM university_master")
            education = cur.fetchall()
            json_list = [{"id": s[0], "name": s[1]} for s in education]
            return jsonify(json_list)

def degree_master():
    with pool.connection()  as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM degree_master")
            degree = cur.fetchall()
            json_list =  [{"id": s[0], "name": s[1]} for s in degree]
            return jsonify(json_list)

def major_master():
    with pool.connection()  as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, major_name FROM major_master")
            major = cur.fetchall()
            json_list = [{"id": s[0], "name": s[1]} for s in major]

            return jsonify(json_list)
def company_master():
    with pool.connection()  as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM company_master")
            company = cur.fetchall()

            json_list= [{"id": s[0], "name": s[1]} for s in company]

            return jsonify(json_list)

def certification_master():
    with pool.connection()  as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM certification_master")
            certification = cur.fetchall()
            json_list =  [{"id": s[0], "name": s[1]} for s in certification]

            return jsonify(json_list)

def login(data):
    with pool.connection()  as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT email_id, password FROM admin_data WHERE email_id = %s and password=%s", (data['email_id'],hash_password(data['password'],'acs57501')))
            user = cur.fetchone()
            if user:
                return jsonify({"message": "Login successful"})
            else:
                raise Exception("Invalid credentials")