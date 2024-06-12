import sqlite3
import logging

# Настройка логгирования
log_file_path = 'input_database.log'
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
# Подключение к базе данных
conn = sqlite3.connect('bank.db')
cursor = conn.cursor()

# Данные для вставки
banks = [
    ('Bank of America', 5000),
    ('Chase', 1000),
    ('Wells Fargo', 2832)
]

users = [
    ('John', 'Doe', '1990-01-01', '1'),
    ('Jane', 'Smith', '1985-05-15', '2'),
    ('Alice', 'Johnson', '1992-07-22', '3'),
    ('Ali', 'John', '1992-07-22', '')
]

accounts = [
    (1, 'credit', 'ID--ABC-123456-ZZZ', 1, banks[0][0], 'PLN', 1000.0, 'gold'),
    (2, 'credit', 'ID--ABC-123458-ZZZ', 1, banks[0][0], 'USD', 1500.0, 'platinum'),
    (3, 'debit', 'ID--ABC-123459-ZZZ', 3, banks[2][0], 'EUR', 700.0, 'gold'),
]

transactions = [
    ('Bank of America', 1, 'Chase', 3, 'USD', 100.0, '2024-06-01 10:00:00'),
    ('Chase', 3, 'Wells Fargo', 4, 'USD', 200.0, '2024-06-02 12:30:00'),
    ('Chase', 3, 'Wells Fargo', 4, 'USD', 400.0, '2024-06-02 12:30:00'),
    ('Wells Fargo', 2, 'Bank of America', 1, 'USD', 150.0, '2024-06-03 14:45:00')
]

# Вставка данных в таблицу Bank
try:
    cursor.executemany('''
        INSERT INTO Bank (name, capital) VALUES (?, ?)
    ''', banks)
    conn.commit()
    logging.info("Данные успешно добавлены в таблицу Bank")
except Exception as e:
    logging.error(f"Ошибка при добавлении данных в таблицу Bank: {e}")
    conn.rollback()

# Вставка данных в таблицу User
try:
    cursor.executemany('''
        INSERT INTO User (name, surname, birth_day, accounts) VALUES (?, ?, ?, ?)
    ''', users)
    conn.commit()
    logging.info("Данные успешно добавлены в таблицу User")
except Exception as e:
    logging.error(f"Ошибка при добавлении данных в таблицу User: {e}")
    conn.rollback()

# Вставка данных в таблицу Account
try:
    cursor.executemany('''
        INSERT INTO Account (user_id, type, account_number, bank_id, bank_name, currency, balance, status) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', accounts)
    conn.commit()
    logging.info("Данные успешно добавлены в таблицу Account")
except Exception as e:
    logging.error(f"Ошибка при добавлении данных в таблицу Account: {e}")
    conn.rollback()

# Вставка данных в таблицу Transaction
try:
    cursor.executemany('''
        INSERT INTO "Transaction" (Bank_sender_name, Account_sender_id, Bank_receiver_name, Account_receiver_id, Sent_Currency, Sent_Amount, Datetime) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', transactions)
    conn.commit()
    logging.info("Данные успешно добавлены в таблицу Transaction")
except Exception as e:
    logging.error(f"Ошибка при добавлении данных в таблицу Transaction: {e}")
    conn.rollback()

# Закрытие соединения
conn.close()

print("Данные успешно добавлены в базу данных.")
