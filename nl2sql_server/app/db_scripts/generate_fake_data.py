import os
import sys
import random
import logging
from urllib.parse import urlparse
import psycopg2
from psycopg2.extras import execute_batch  # For bulk inserts
from faker import Faker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("database.log")
    ]
)

# Get DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL is not set in environment variables!")

# Parse DATABASE_URL
parsed_url = urlparse(DATABASE_URL)
DB_HOST = parsed_url.hostname
DB_PORT = parsed_url.port
DB_NAME = parsed_url.path[1:]
DB_USER = parsed_url.username
DB_PASSWORD = parsed_url.password

# Initialize Faker
fake = Faker()

# Connect to PostgreSQL
def create_connection():
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        logging.info(f"Connected to the database: {DB_NAME}")
        return connection
    except Exception as e:
        logging.error(f"Error connecting to database {DB_NAME}: {e}")
        return None

# Helper to fetch all IDs from a table
def fetch_all_ids(cursor, table):
    # Map table name to its ID column
    id_columns = {
        "categories": "category_id",
        "users": "user_id",
        "products": "product_id",
        "orders": "order_id"
    }

    id_column = id_columns.get(table)
    if not id_column:
        raise Exception(f"No ID column mapping found for table '{table}'.")

    cursor.execute(f"SELECT {id_column} FROM {table};")
    results = cursor.fetchall()
    return [row[0] for row in results]

# Main fake data generator
def generate_fake_data(num_records):
    connection = create_connection()
    if connection is None:
        return

    try:
        cursor = connection.cursor()

        # Insert fake categories if none exist
        cursor.execute("SELECT COUNT(*) FROM categories;")
        if cursor.fetchone()[0] == 0:
            logging.info("Inserting default categories...")
            categories = ["Electronics", "Clothing", "Books", "Home & Kitchen", "Sports"]
            categories_data = [(category, fake.text(max_nb_chars=100)) for category in categories]
            cursor.executemany(
                "INSERT INTO categories (name, description) VALUES (%s, %s)",
                categories_data
            )
        
        connection.commit()

        # Fetch category IDs
        category_ids = fetch_all_ids(cursor, "categories")

        # Insert fake users
        logging.info(f"Inserting {num_records} fake users...")
        users_data = [
            (fake.user_name(), fake.email(), fake.password()) for _ in range(num_records)
        ]
        execute_batch(
            cursor,
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            users_data
        )

        connection.commit()

        # Fetch user IDs
        user_ids = fetch_all_ids(cursor, "users")

        # Insert fake products
        logging.info(f"Inserting {num_records} fake products...")
        real_product_names = [
            "Wireless Mouse", "Bluetooth Headphones", "Gaming Keyboard", "Smartphone", "4K TV",
            "Laptop", "Smartwatch", "Coffee Maker", "Electric Kettle", "Gaming Chair", "Air Conditioner"
        ]
        products_data = [
            (random.choice(category_ids), random.choice(real_product_names), fake.text(max_nb_chars=200),
            round(random.uniform(10.0, 500.0), 2), random.randint(1, 100)) for _ in range(num_records)
        ]
        execute_batch(
            cursor,
            "INSERT INTO products (category_id, name, description, price, stock_quantity) VALUES (%s, %s, %s, %s, %s)",
            products_data
        )

        connection.commit()

        # Fetch product IDs
        product_ids = fetch_all_ids(cursor, "products")

        # Insert fake orders
        logging.info(f"Inserting {num_records} fake orders...")
        orders_data = [
            (random.choice(user_ids), round(random.uniform(20.0, 1000.0), 2), 'pending', fake.date_this_year()) for _ in range(num_records)
        ]
        execute_batch(
            cursor,
            "INSERT INTO orders (user_id, total_amount, status, order_date) VALUES (%s, %s, %s, %s)",
            orders_data
        )

        connection.commit()

        # Fetch order IDs
        order_ids = fetch_all_ids(cursor, "orders")

        # Insert fake order items
        logging.info(f"Inserting {num_records * 2} fake order items...")
        order_items_data = [
            (random.choice(order_ids), random.choice(product_ids), random.randint(1, 5),
             round(random.uniform(10.0, 100.0), 2)) for _ in range(num_records * 2)
        ]
        execute_batch(
            cursor,
            "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
            order_items_data
        )

        # Insert fake reviews
        logging.info(f"Inserting {num_records} fake reviews...")
        reviews_data = [
            (random.choice(user_ids), random.choice(product_ids), random.randint(1, 5), fake.text(max_nb_chars=200))
            for _ in range(num_records)
        ]
        execute_batch(
            cursor,
            "INSERT INTO reviews (user_id, product_id, rating, comment) VALUES (%s, %s, %s, %s)",
            reviews_data
        )

        connection.commit()
        
        # Insert fake payments
        logging.info(f"Inserting {num_records} fake payments...")
        payments_data = [
            (random.choice(order_ids), random.choice(['Credit Card', 'PayPal', 'Bank Transfer']), round(random.uniform(10.0, 1000.0), 2), 'completed', fake.date_this_year())
            for _ in range(num_records)
        ]
        execute_batch(
            cursor,
            "INSERT INTO payments (order_id, payment_method, amount, payment_status, payment_date) VALUES (%s, %s, %s, %s, %s)",
            payments_data
        )

        # Insert fake shipping details
        logging.info(f"Inserting {num_records} fake shipping details...")
        shipping_data = [
            (random.choice(order_ids), fake.address(), random.choice(['Standard', 'Express', 'Next Day']), 'shipped', fake.date_this_year())
            for _ in range(num_records)
        ]
        execute_batch(
            cursor,
            "INSERT INTO shipping (order_id, address, shipping_method, shipping_status, shipping_date) VALUES (%s, %s, %s, %s, %s)",
            shipping_data
        )

        # Insert fake inventory transactions
        logging.info(f"Inserting {num_records} fake inventory transactions...")
        inventory_transactions_data = [
            (random.choice(product_ids), random.randint(1, 10), random.choice(['sale', 'restock']), fake.date_this_year())
            for _ in range(num_records)
        ]
        execute_batch(
            cursor,
            "INSERT INTO inventory_transactions (product_id, quantity, transaction_type, transaction_date) VALUES (%s, %s, %s, %s)",
            inventory_transactions_data
        )

        # Insert coupons with unique codes
        logging.info(f"Inserting {num_records} fake coupons...")
        coupons_data = [
            (fake.word() + str(random.randint(1000, 9999)), random.randint(5, 50), fake.date_this_year(), fake.date_this_year(), True)
            for _ in range(num_records)
        ]
        execute_batch(
            cursor,
            "INSERT INTO coupons (code, discount_percentage, valid_from, valid_until, is_active) VALUES (%s, %s, %s, %s, %s)",
            coupons_data
        )

        # Insert fake order_coupons
        logging.info(f"Inserting {num_records} fake order coupons...")
        order_coupons_data = [
            (random.choice(order_ids), random.choice([i for i in range(1, num_records + 1)]))
            for _ in range(num_records)
        ]
        execute_batch(
            cursor,
            "INSERT INTO order_coupons (order_id, coupon_id) VALUES (%s, %s)",
            order_coupons_data
        )

        connection.commit()
        logging.info("Fake data inserted successfully.")

    except Exception as e:
        logging.error(f"Error generating fake data: {e}")
    finally:
        cursor.close()
        connection.close()
        logging.info("Database connection closed.")

if __name__ == "__main__":
    try:
        num_records = 200  # default
        if num_records < 100 or num_records > 1000:
            logging.error("Please provide a number between 100 and 1000.")
            sys.exit(1)
    except ValueError:
        logging.error("Invalid number format for num_records.")
        sys.exit(1)
    
    generate_fake_data(num_records)
