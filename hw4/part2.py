import sqlite3
import logging
from functools import wraps
from datetime import datetime
import csv
import re
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


API_KEY = 'your_api_key_here'
EXCHANGE_RATE_API_URL = 'https://api.freecurrencyapi.com/v1/latest'


# Database connection decorator
def db_connection(func):
    @wraps(func)
    def with_connection(*args, **kwargs):
        conn = sqlite3.connect('bank.db')
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}")
            conn.rollback()
            return f"Failure: {e}"
        finally:
            conn.close()

    return with_connection


# Helper functions for validation
def validate_user_full_name(user_full_name):
    """
    Validate and parse user full name.
    """
    name_parts = re.findall(r'[a-zA-Z]+', user_full_name)
    if len(name_parts) < 2:
        raise ValueError("Invalid user full name!")
    return name_parts[0], " ".join(name_parts[1:])


def validate_strict_field(value, allowed_values, field_name):
    """
    Validate fields with a strict set of allowed values.
    """
    if value not in allowed_values:
        raise ValueError(f"Not allowed value '{value}' for field '{field_name}'!")


def validate_account_number(account_number):
    """
    Validate and format account number.
    """
    account_number = re.sub(r'[%#_?&]', '-', account_number)
    if len(account_number) != 18:
        raise ValueError("Too little/many chars!")
    if not account_number.startswith('ID--'):
        raise ValueError("Wrong format!")

    pattern = re.compile(r'[a-zA-Z]{1,3}-\d+-[a-zA-Z0-9]+')
    if not pattern.search(account_number):
        raise ValueError("Broken ID!")

    return account_number


def get_current_time():
    """
    Get the current time in the required format.
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


# Functions to add data to the database
@db_connection
def add_user(conn, *users):
    cursor = conn.cursor()
    for user in users:
        name, surname = validate_user_full_name(user['user_full_name'])
        cursor.execute('''
            INSERT INTO User (name, surname, birth_day, accounts) VALUES (?, ?, ?, ?)
        ''', (name, surname, user.get('birth_day', None), user.get('accounts', '')))
    logging.info("Users added successfully")
    return "Success: Users added successfully"


# Function to add a bank with uniqueness check
@db_connection
def add_bank(conn, name):
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO Bank (name) VALUES (?)
        ''', (name,))
        logging.info(f"Bank '{name}' added successfully")
        return "Success: Bank added successfully"
    except sqlite3.IntegrityError:
        logging.error(f"Failed to add bank '{name}': Bank with the same name already exists")
        return f"Failure: Bank '{name}' already exists"

# Function to add an account with uniqueness check
@db_connection
def add_account(conn, user_id, type, account_number, bank_id, currency, amount, status):
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO Account (user_id, type, account_number, bank_id, currency, amount, status) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, type, account_number, bank_id, currency, amount, status))
        logging.info(f"Account '{account_number}' added successfully")
        return "Success: Account added successfully"
    except sqlite3.IntegrityError:
        logging.error(f"Failed to add account '{account_number}': Account with the same account number already exists")
        return f"Failure: Account '{account_number}' already exists"



# Functions to add data from CSV files
@db_connection
def add_users_from_csv(conn, csv_file_path):
    cursor = conn.cursor()
    with open(csv_file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            name, surname = validate_user_full_name(row['user_full_name'])
            cursor.execute('''
                INSERT INTO User (name, surname, birth_day, accounts) VALUES (?, ?, ?, ?)
            ''', (name, surname, row.get('birth_day', None), row.get('accounts', '')))
    logging.info("Users added from CSV successfully")
    return "Success: Users added from CSV successfully"


@db_connection
def add_banks_from_csv(conn, csv_file_path):
    cursor = conn.cursor()
    with open(csv_file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute('''
                INSERT INTO Bank (name) VALUES (?)
            ''', (row['name'],))
    logging.info("Banks added from CSV successfully")
    return "Success: Banks added from CSV successfully"


@db_connection
def add_accounts_from_csv(conn, csv_file_path):
    cursor = conn.cursor()
    with open(csv_file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            account_number = validate_account_number(row['account_number'])
            validate_strict_field(row['type'], ['credit', 'debit'], 'type')
            validate_strict_field(row['status'], ['gold', 'silver', 'platinum'], 'status')
            cursor.execute('''
                INSERT INTO Account (user_id, type, account_number, bank_id, currency, amount, status) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['user_id'], row['type'], account_number,
                row['bank_id'], row['currency'], row['amount'],
                row['status']
            ))
    logging.info("Accounts added from CSV successfully")
    return "Success: Accounts added from CSV successfully"


# Functions to modify and delete data
@db_connection
def modify_user(conn, user_id, **updates):
    cursor = conn.cursor()
    set_clause = ", ".join(f"{key} = ?" for key in updates.keys())
    values = list(updates.values()) + [user_id]
    cursor.execute(f'''
        UPDATE User SET {set_clause} WHERE id = ?
    ''', values)
    logging.info(f"User {user_id} modified successfully")
    return f"Success: User {user_id} modified successfully"


@db_connection
def delete_user(conn, user_id):
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM User WHERE id = ?
    ''', (user_id,))
    logging.info(f"User {user_id} deleted successfully")
    return f"Success: User {user_id} deleted successfully"


@db_connection
def modify_bank(conn, bank_id, **updates):
    cursor = conn.cursor()
    set_clause = ", ".join(f"{key} = ?" for key in updates.keys())
    values = list(updates.values()) + [bank_id]
    cursor.execute(f'''
        UPDATE Bank SET {set_clause} WHERE id = ?
    ''', values)
    logging.info(f"Bank {bank_id} modified successfully")
    return f"Success: Bank {bank_id} modified successfully"


@db_connection
def delete_bank(conn, bank_id):
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM Bank WHERE id = ?
    ''', (bank_id,))
    logging.info(f"Bank {bank_id} deleted successfully")
    return f"Success: Bank {bank_id} deleted successfully"


@db_connection
def modify_account(conn, account_id, **updates):
    cursor = conn.cursor()
    set_clause = ", ".join(f"{key} = ?" for key in updates.keys())
    values = list(updates.values()) + [account_id]
    cursor.execute(f'''
        UPDATE Account SET {set_clause} WHERE id = ?
    ''', values)
    logging.info(f"Account {account_id} modified successfully")
    return f"Success: Account {account_id} modified successfully"


@db_connection
def delete_account(conn, account_id):
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM Account WHERE id = ?
    ''', (account_id,))
    logging.info(f"Account {account_id} deleted successfully")
    return f"Success: Account {account_id} deleted successfully"


# Functions to perform money transfers
def get_exchange_rate(from_currency, to_currency):
    response = requests.get(EXCHANGE_RATE_API_URL, params={'apikey': API_KEY, 'base_currency': from_currency})
    data = response.json()
    return data['data'][to_currency]


@db_connection
def perform_money_transfer(conn, sender_account_id, receiver_account_id, amount):
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Account WHERE id = ?', (sender_account_id,))
    sender_account = cursor.fetchone()
    cursor.execute('SELECT * FROM Account WHERE id = ?', (receiver_account_id,))
    receiver_account = cursor.fetchone()

    if not sender_account or not receiver_account:
        logging.error("Invalid account details")
        return "Failure: Invalid account details"

    sender_balance = sender_account[6]
    sender_currency = sender_account[4]
    receiver_currency = receiver_account[4]

    if sender_balance < amount:
        logging.error("Insufficient balance")
        return "Failure: Insufficient balance"

    if sender_currency != receiver_currency:
        exchange_rate = get_exchange_rate(sender_currency, receiver_currency)
        converted_amount = amount * exchange_rate
    else:
        converted_amount = amount

    new_sender_balance = sender_balance - amount
    new_receiver_balance = receiver_account[6] + converted_amount

    cursor.execute('UPDATE Account SET amount = ? WHERE id = ?', (new_sender_balance, sender_account_id))
    cursor.execute('UPDATE Account SET amount = ? WHERE id = ?', (new_receiver_balance, receiver_account_id))

    datetime_now = get_current_time()

    cursor.execute('''
        INSERT INTO "Transaction" (Bank_sender_name, Account_sender_id, Bank_receiver_name, Account_receiver_id, Sent_Currency, Sent_Amount, Datetime) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        sender_account[3], sender_account_id,
        receiver_account[3], receiver_account_id,
        sender_currency, amount,
        datetime_now
    ))

    logging.info(f"Money transferred from account {sender_account_id} to account {receiver_account_id}")
    return f"Success: Money transferred from account {sender_account_id} to account {receiver_account_id}"
