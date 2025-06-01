import psycopg2
import json
import os
from dotenv import load_dotenv
load_dotenv()

# Load JSON
with open("customer_data.json") as f:
    data = json.load(f)["customer_profile"]

# Connect to PostgreSQL
conn = psycopg2.connect(os.getenv("POSTGRES"))
cursor = conn.cursor()

# Insert into customers
personal = data["personal_info"]
cursor.execute("""
    INSERT INTO customers (customer_id, first_name, last_name, gender, date_of_birth, age, marital_status, city, state, employment_status, occupation, annual_income)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
""", (
    personal["customer_id"], personal["first_name"], personal["last_name"], personal["gender"],
    personal["date_of_birth"], personal["age"], personal["marital_status"], personal["city"],
    personal["state"], personal["employment_status"], personal["occupation"], personal["annual_income"]
))

# Insert contact info
contact = data["contact_info"]
cursor.execute("""
    INSERT INTO contact_info (customer_id, email, phone_number)
    VALUES (%s, %s, %s)
""", (personal["customer_id"], contact["email"], contact["phone_number"]))

# Similarly insert into other tables...

conn.commit()
cursor.close()
conn.close()
