import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_db():
    try:

        conn = psycopg2.connect(
    user="postgres.sbykicbslggbbmvwtmhl",
    password=os.getenv("DATABASE_PSWD"),
    host="aws-1-ap-northeast-1.pooler.supabase.com",
    port=5432,
    dbname="postgres"
)
        print("DB OK!!")
        return conn, conn.cursor()

    except Exception as e:
        print("DB not connected!!")
        print("Error:", e)
        return None, None


