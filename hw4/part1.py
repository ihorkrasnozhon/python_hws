import sqlite3
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_database(unique_name_surname):
    try:
        # Connect to the SQLite database (or create it if it doesn't exist)
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()

        # Create Bank table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Bank (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                capital REAL DEFAULT 0.0
            )
        ''')

        # Create Transaction table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "Transaction" (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Bank_sender_name TEXT NOT NULL,
                Account_sender_id INTEGER NOT NULL,
                Bank_receiver_name TEXT NOT NULL,
                Account_receiver_id INTEGER NOT NULL,
                Sent_Currency TEXT NOT NULL,
                Sent_Amount REAL NOT NULL,
                Datetime TEXT
            )
        ''')

        # Create User table
        user_table_creation_query = '''
            CREATE TABLE IF NOT EXISTS User (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                surname TEXT NOT NULL,
                birth_day TEXT,
                accounts TEXT NOT NULL
            '''
        if unique_name_surname:
            user_table_creation_query += ', UNIQUE (name, surname)'
        user_table_creation_query += ')'
        cursor.execute(user_table_creation_query)

        # Create Account table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Account (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL CHECK (type IN ('credit', 'debit')),
                account_number TEXT NOT NULL UNIQUE,
                bank_id INTEGER NOT NULL,
                currency TEXT NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('gold', 'silver', 'platinum')),
                FOREIGN KEY (user_id) REFERENCES User(id),
                FOREIGN KEY (bank_id) REFERENCES Bank(id)
            )
        ''')

        # Commit the transaction and close the connection
        conn.commit()
        conn.close()
        logging.info("Database created successfully")
    except Exception as e:
        logging.error(f"Error creating database: {e}")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Initialize the database.')
    parser.add_argument('--unique-name-surname', action='store_true', help='Ensure unique combinations of User Name and Surname.')
    args = parser.parse_args()

    # Create the database
    create_database(args.unique_name_surname)
