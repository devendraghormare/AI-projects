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

def create_connection(database=DB_NAME):
    try:
        url = f"{parsed_url.scheme}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{database}"
        connection = psycopg2.connect(url)
        logging.info(f"Successfully connected to the database: {database}")
        return connection
    except Exception as e:
        logging.error(f"Error connecting to database {database}: {e}")
        return None

def create_database_if_not_exists():
    connection = create_connection("postgres")
    if connection is None:
        return
    
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s;", (DB_NAME,))
        if cursor.fetchone():
            logging.info(f"Database '{DB_NAME}' already exists.")
        else:
            logging.info(f"Database '{DB_NAME}' does not exist. Creating...")
            cursor.execute(f"CREATE DATABASE {DB_NAME};")
            logging.info(f"Database '{DB_NAME}' created successfully.")
        connection.commit()
    except Exception as e:
        logging.error(f"Error checking or creating database: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

create_tables_sql = """
-- Your full SQL schema (same as before, no changes needed)
-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    role VARCHAR(50) DEFAULT 'customer'
);

-- Categories table
CREATE TABLE IF NOT EXISTS categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    category_id INT REFERENCES categories(category_id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order Items table
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id INT REFERENCES products(product_id) ON DELETE CASCADE,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

-- Reviews table
CREATE TABLE IF NOT EXISTS reviews (
    review_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    product_id INT REFERENCES products(product_id) ON DELETE CASCADE,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Payments table
CREATE TABLE IF NOT EXISTS payments (
    payment_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(order_id) ON DELETE CASCADE,
    payment_method VARCHAR(50),
    amount DECIMAL(10, 2) NOT NULL,
    payment_status VARCHAR(50) DEFAULT 'pending',
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Shipping table
CREATE TABLE IF NOT EXISTS shipping (
    shipping_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(order_id) ON DELETE CASCADE,
    address VARCHAR(255) NOT NULL,
    shipping_method VARCHAR(50),
    shipping_status VARCHAR(50) DEFAULT 'pending',
    shipping_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inventory Transactions table
CREATE TABLE IF NOT EXISTS inventory_transactions (
    transaction_id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(product_id) ON DELETE CASCADE,
    quantity INT NOT NULL,
    transaction_type VARCHAR(50),
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Coupons table
CREATE TABLE IF NOT EXISTS coupons (
    coupon_id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    discount_percentage INT CHECK (discount_percentage > 0 AND discount_percentage <= 100),
    valid_from TIMESTAMP,
    valid_until TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Order Coupon Mapping table
CREATE TABLE IF NOT EXISTS order_coupons (
    order_id INT REFERENCES orders(order_id) ON DELETE CASCADE,
    coupon_id INT REFERENCES coupons(coupon_id) ON DELETE CASCADE,
    PRIMARY KEY (order_id, coupon_id)
);
"""

def create_tables():
    create_database_if_not_exists()
    connection = create_connection(DB_NAME)
    if connection is None:
        return
    
    try:
        cursor = connection.cursor()
        logging.info("Starting to create tables...")
        cursor.execute(create_tables_sql)
        connection.commit()
        logging.info("Tables created successfully.")
    except Exception as e:
        logging.error(f"Error creating tables: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            logging.info("Database connection closed.")

if __name__ == "__main__":
    create_tables()
