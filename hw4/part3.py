import sqlite3
import logging
import random
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database connection decorator
def db_connection(func):
    def with_connection(*args, **kwargs):
        conn = sqlite3.connect('bank.db')
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    return with_connection

# Function to randomly choose users with discounts
@db_connection
def get_users_with_discounts(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM User ORDER BY RANDOM() LIMIT ?', (random.randint(1, 10),))
    user_ids = [row[0] for row in cursor.fetchall()]
    discounts = [25, 30, 50]
    user_discounts = {user_id: random.choice(discounts) for user_id in user_ids}
    return user_discounts

# Function to get full names of users with debts
@db_connection
def get_users_with_debts(conn):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, surname FROM User
        WHERE id IN (
            SELECT DISTINCT user_id FROM Account
            WHERE amount < 0
        )
    ''')
    users_with_debts = cursor.fetchall()
    return users_with_debts

# Function to get the bank with the biggest capital
@db_connection
def get_bank_with_biggest_capital(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM Bank ORDER BY capital DESC LIMIT 1')
    bank_with_biggest_capital = cursor.fetchone()
    return bank_with_biggest_capital

# Function to get the bank serving the oldest client
@db_connection
def get_bank_serving_oldest_client(conn):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT b.id, b.name FROM Bank b
        JOIN Account a ON b.id = a.bank_id
        WHERE a.user_id = (
            SELECT id FROM User ORDER BY birth_day ASC LIMIT 1
        )
    ''')
    bank_serving_oldest_client = cursor.fetchone()
    return bank_serving_oldest_client

# Function to get the bank with the highest number of unique users with outbound transactions
@db_connection
def get_bank_with_highest_outbound_transactions(conn):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT b.id, b.name FROM Bank b
        JOIN Account a ON b.id = a.bank_id
        JOIN "Transaction" t ON a.id = t.account_sender_id
        GROUP BY b.id
        ORDER BY COUNT(DISTINCT a.user_id) DESC
        LIMIT 1
    ''')
    bank_with_highest_outbound_transactions = cursor.fetchone()
    return bank_with_highest_outbound_transactions

# Function to delete users and accounts without full information
@db_connection
def delete_incomplete_users_and_accounts(conn):
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM User WHERE name IS NULL OR surname IS NULL
    ''')
    cursor.execute('''
        DELETE FROM Account WHERE user_id NOT IN (SELECT id FROM User)
    ''')
    logging.info("Incomplete users and accounts deleted successfully")

# Function to get transactions of a particular user for the past 3 months
@db_connection
def get_user_transactions_past_3_months(conn, user_id):
    cursor = conn.cursor()
    three_months_ago = datetime.now() - timedelta(days=90)
    cursor.execute('''
        SELECT * FROM "Transaction"
        WHERE account_sender_id = ? AND datetime >= ?
    ''', (user_id, three_months_ago))
    user_transactions = cursor.fetchall()
    return user_transactions
