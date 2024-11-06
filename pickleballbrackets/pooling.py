import os
import psycopg2
from psycopg2 import sql, pool
# Database connection parameters
db_params = {
    'dbname': 'pooling_db',
    'user': 'postgres',
    'password': 'noman',
    'host': 'localhost',  # or your database host
    'port': 5432         
}
# Initialize connection pool
connection_pool = pool.SimpleConnectionPool(1, 10, **db_params)
# SQL statements for creating tables
create_table_sql = """
CREATE TABLE IF NOT EXISTS shipment_charges (
    id SERIAL PRIMARY KEY,
    tracking_number VARCHAR(50) NOT NULL,
    original_weight DECIMAL(10, 2),
    billed_weight DECIMAL(10, 2),
    zone INTEGER,
    amount DECIMAL(10, 2) NOT NULL,
    amount_local DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    currency_local VARCHAR(10) NOT NULL,
    arrives_by DATE,
    attributes TEXT,
    carrier_account VARCHAR(100),
    estimated_days INTEGER,
    object_owner VARCHAR(100) NOT NULL,
    shipment VARCHAR(100) NOT NULL,
    provider VARCHAR(100) NOT NULL,
    object_id VARCHAR(100) NOT NULL UNIQUE,
    object_created TIMESTAMP NOT NULL,
    test BOOLEAN,
    recipient_name VARCHAR(100),
    recipient_company VARCHAR(100),
    recipient_address_line_1 VARCHAR(255),
    recipient_city VARCHAR(100),
    shipper_country VARCHAR(100),
    shipper_zip_code VARCHAR(20),
    shipper_state VARCHAR(100),
    shipper_city VARCHAR(100),
    shipper_address_line_1 VARCHAR(255),
    shipper_company VARCHAR(100),
    shipper_name VARCHAR(100)
);
"""
create_log_table_sql = """
CREATE TABLE IF NOT EXISTS log_detail (
    id SERIAL PRIMARY KEY,
    log TEXT NOT NULL
);
"""
# SQL statement with placeholders for batch insert
insert_data_sql = """
INSERT INTO shipment_charges (
    tracking_number, original_weight, billed_weight, zone, amount, amount_local,
    currency, currency_local, arrives_by, attributes, carrier_account,
    estimated_days, object_owner, shipment, provider, object_id,
    object_created, test, recipient_name, recipient_company, recipient_address_line_1,
    recipient_city, shipper_country, shipper_zip_code, shipper_state,
    shipper_city, shipper_address_line_1, shipper_company, shipper_name
) VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s, %s
);
"""
# Demo data to be inserted
demo_data = [
    ("537686940816", 0.88, 1.00, 1, 4.10, 4.10, "USD", "USD", "2024-08-16", "", "Account1", 3, "Owner1", "Shipment1", "DHL eComm", "object_id_1", "2024-08-16 10:00:00", False, "John Doe", "Recipient Company", "123 Main St", "Recipient City", "USA", "12345", "CA", "Shipper City", "456 Elm St", "Shipper Company", "Shipper Name"),
    ("537686940816", 0.44, 1.00, 1, 75.57, 75.57, "USD", "USD", "2024-08-16", "", "Account1", 3, "Owner1", "Shipment1", "DHL eComm", "object_id_2", "2024-08-16 10:00:00", False, "Jane Smith", "Another Company", "789 Oak St", "Another City", "USA", "67890", "NY", "Shipper City", "101 Pine St", "Another Shipper Company", "Another Shipper Name")
]
def create_table(conn, create_table_sql):
    try:
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        conn.commit()
        print("Table created successfully")
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        cursor.close()
def insert_batch_data(conn, insert_data_sql, data):
    try:
        cursor = conn.cursor()
        cursor.executemany(insert_data_sql, data)
        conn.commit()
        print("Demo data inserted successfully")
    except Exception as e:
        print(f"Error inserting demo data: {e}")
    finally:
        cursor.close()
# Main function
def main():
    # Create a new connection from the pool
    conn = connection_pool.getconn()
    try:
        # Create tables
        create_table(conn, create_table_sql)  
        create_table(conn, create_log_table_sql)  
        # Insert demo data into shipment_charges
        insert_batch_data(conn, insert_data_sql, demo_data)
    finally:
        # Return connection to the pool
        connection_pool.putconn(conn)
if __name__ == '__main__':
    main() 