import os
import logging
from urllib.parse import urlparse
import psycopg2
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("database.log")
    ]
)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL is not set in environment variables!")

parsed_url = urlparse(DATABASE_URL)

DB_HOST = parsed_url.hostname
DB_PORT = parsed_url.port
DB_NAME = parsed_url.path[1:]  
DB_USER = parsed_url.username
DB_PASSWORD = parsed_url.password

def create_connection():
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        logging.info(f"Successfully connected to the database: {DB_NAME}")
        return connection
    except Exception as e:
        logging.error(f"Error connecting to database {DB_NAME}: {e}")
        return None

def delete_all_records():
    connection = create_connection()
    if connection is None:
        return
    
    try:
        cursor = connection.cursor()
        cursor.execute("SET session_replication_role = 'replica';")

        tables = [
            "order_coupons",
            "payments",
            "shipping",
            "inventory_transactions",
            "order_items",
            "reviews",
            "orders",
            "products",
            "categories",
            "coupons",
            "users"
        ]
        
        for table in tables:
            try:
                logging.info(f"Deleting records from table: {table}")
                cursor.execute(f"DELETE FROM {table};")
            except Exception as e:
                logging.warning(f"Skipping table {table} due to error: {e}")

        cursor.execute("SET session_replication_role = 'origin';")

        connection.commit()
        logging.info("All records deleted successfully.")

    except Exception as e:
        logging.error(f"Error deleting records: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            logging.info("Database connection closed.")

if __name__ == "__main__":
    delete_all_records()
