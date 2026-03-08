import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()
def get_db():
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        print("DB OK!!")
        return conn, conn.cursor()
    except Exception as e:
        print("DB not connected!!")
        print("Error:", e)
        return None, None
