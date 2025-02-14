import json

from flask import jsonify
from psycopg_pool import ConnectionPool


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
                    jsonify(
                        {"id": a[0], "first_name": a[1], "last_name": a[2], "email_id": a[3], "phone": a[4],
                         "address": a[5], "location_id": a[6],
                         "education": [{"id": e[0], "education_id": e[1], "degree_id": e[2], "major_id": e[3],
                                        "start_date": e[4], "end_date": e[5]} for e in education],
                         "experience": [
                             {"id": e[0], "company_id": e[1], "title": e[2], "start_date": e[3], "end_date": e[4]}
                             for e in experience],
                         "skills": [{"id": s[0], "skill_id": s[1]} for s in skills],
                         "certifications": [{"id": c[0], "certification_id": c[1], "issuing_date": c[2]} for c in
                                            certifications]
                         }
                    ))
                return json.dumps(json_list)

            else:
                cur.execute("SELECT * FROM Applicant_data WHERE id = %s;", (user_id,))
                a = cur.fetchone()
                education, experience, skills, certifications = get_entities(user_id)
                jsonify(
                    {"id": a[0], "first_name": a[1], "last_name": a[2], "email_id": a[3], "phone": a[4],
                     "address": a[5], "location_id": a[6],
                     "education": [{"id": e[0], "education_id": e[1], "degree_id": e[2], "major_id": e[3],
                                    "start_date": e[4], "end_date": e[5]} for e in education],
                     "experience": [
                         {"id": e[0], "company_id": e[1], "title": e[2], "start_date": e[3], "end_date": e[4]}
                         for e in experience],
                     "skills": [{"id": s[0], "skill_id": s[1]} for s in skills],
                     "certifications": [{"id": c[0], "certification_id": c[1], "issuing_date": c[2]} for c in
                                        certifications]
                     }
                )

def get_entities(user_id):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT e.id, e.education_id, e.degree_id, e.major_id, e.start_date, e.end_date
                FROM Applicant_education e
                WHERE e.applicant_id = %s;
            """, (user_id,))
            education = cur.fetchall()

            cur.execute("""
                SELECT e.id, e.company_id, e.title, e.start_date, e.end_date
                FROM Applicant_experience e
                WHERE e.applicant_id = %s;
            """, (user_id,))
            experience = cur.fetchall()

            cur.execute("""
                SELECT s.id, s.skill_id
                FROM Applicant_skills s
                WHERE s.applicant_id = %s;
            """, (user_id,))
            skills = cur.fetchall()

            cur.execute("""
                SELECT c.id, c.certification_id, c.issuing_date
                FROM Applicant_Certification c
                WHERE c.applicant_id = %s;
            """, (user_id,))
            certifications = cur.fetchall()

            return education, experience, skills, certifications

def create_applicants(data):
    with pool.connection()  as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO Applicant_data (first_name, last_name, email_id, phone, address, location_id)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
            """, (data['first_name'], data['last_name'], data['email_id'], data['phone'], data.get('address', None),
                  data['location_id']))
            user_id = cur.fetchone()[0]

            for edu in data.get('education', []):
                cur.execute("""
                            INSERT INTO Applicant_education (applicant_id, education_id, degree_id, major_id, start_date, end_date)
                            VALUES (%s, %s, %s, %s, %s, %s);
                        """, (user_id, edu['education_id'], edu['degree_id'], edu['major_id'], edu['start_date'],
                              edu['end_date']))

            for exp in data.get('experience', []):
                cur.execute("""
                            INSERT INTO Applicant_experience (applicant_id, company_id, start_date, end_date)
                            VALUES (%s, %s, %s, %s);
                        """, (user_id, exp['company_id'], exp['start_date'], exp.get('end_date', None)))

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
                        INSERT INTO Applicant_experience (applicant_id, company_id, start_date, end_date)
                        VALUES (%s, %s, %s, %s);
                    """, (user_id, exp['company_id'], exp['start_date'], exp.get('end_date', None)))

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
            return cur.fetchall()