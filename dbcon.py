
import psycopg2
from dotenv import load_dotenv
import os


load_dotenv()
def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS')
    )
    db_connection_string = os.environ.get('DB_CONNECTION_STRING')
    return conn#db_connection_string#conn