from flask import jsonify
from psycopg_pool import ConnectionPool


DB_CONFIG = "dbname=Career_Management_System user=postgres password=Chottu@1125 host=localhost port=5432"
pool = ConnectionPool(conninfo=DB_CONFIG, min_size=1, max_size=10)


def get_applicants(user_id=None):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            if user_id is None:
                cur.execute("SELECT * FROM Applicant_data")
                applicants = cur.fetchall()
                return jsonify([
                    {"id": a[0], "first_name": a[1], "last_name": a[2], "email_id": a[3], "phone": a[4],
                     "address": a[5], "location_id": a[6]}
                    for a in applicants
                ])
            else:
                cur.execute("SELECT * FROM Applicant_data WHERE id = %s", (user_id,))
                applicant = cur.fetchone()
                return jsonify({"id": applicant[0], "first_name": applicant[1], "last_name": applicant[2],
                                 "email_id": applicant[3], "phone": applicant[4], "address": applicant[5],
                                 "location_id": applicant[6]})


def create_applicants(data):
    with pool.connection()  as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO Applicant_data (first_name, last_name, email_id, phone, address) 
                VALUES (%s, %s, %s, %s, %s) RETURNING id
            """, (data["first_name"], data["last_name"], data["email_id"], data["phone"], data.get("address")))
            user_id = cur.fetchone()[0]
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
            conn.commit()
    if updated:
        return jsonify({"id":user_id})
    else:
        raise Exception("User not found")

def delete_applicant(user_id):
    with pool.connection()  as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Applicant_data WHERE id = %s RETURNING id", (user_id,))
            deleted = cur.fetchone()
            conn.commit()
    if deleted:
        return jsonify({"message": f"User {user_id} deleted"})
    else:
        raise Exception("User not found")