import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_db():
    try:
        scrt_db = os.getenv("DATABASE_URL")

        conn = psycopg2.connect(scrt_db, sslmode="require")
        print("DB OK!!")
        return conn, conn.cursor()

    except Exception as e:
        print("DB not connected!!")
        print("Error:", e)
        return None, None
