import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('bank.db')
cursor = conn.cursor()

# Данные для вставки
banks = [
    ('Bank of America',),
    ('Chase',),
    ('Wells Fargo',)
]

users = [
    ('John', 'Doe', '1990-01-01', '1,2'),
    ('Jane', 'Smith', '1985-05-15', '3'),
    ('Alice', 'Johnson', '1992-07-22', '4,5')
]

accounts = [
    (1, 'credit', '1234567890', 1, 'USD', 1000.0, 'gold'),
    (1, 'debit', '0987654321', 2, 'USD', 500.0, 'silver'),
    (2, 'credit', '1122334455', 1, 'USD', 1500.0, 'platinum'),
    (3, 'debit', '2233445566', 3, 'USD', 700.0, 'gold'),
    (3, 'credit', '3344556677', 2, 'USD', 1200.0, 'silver')
]

transactions = [
    ('Bank of America', 1, 'Chase', 3, 'USD', 100.0, '2024-06-01 10:00:00'),
    ('Chase', 3, 'Wells Fargo', 4, 'USD', 200.0, '2024-06-02 12:30:00'),
    ('Wells Fargo', 4, 'Bank of America', 1, 'USD', 150.0, '2024-06-03 14:45:00')
]

# Вставка данных в таблицу Bank
cursor.executemany('''
    INSERT INTO Bank (name) VALUES (?)
''', banks)

# Вставка данных в таблицу User
cursor.executemany('''
    INSERT INTO User (name, surname, birth_day, accounts) VALUES (?, ?, ?, ?)
''', users)

# Вставка данных в таблицу Account
cursor.executemany('''
    INSERT INTO Account (user_id, type, account_number, bank_id, currency, amount, status) VALUES (?, ?, ?, ?, ?, ?, ?)
''', accounts)

# Вставка данных в таблицу Transaction
cursor.executemany('''
    INSERT INTO "Transaction" (Bank_sender_name, Account_sender_id, Bank_receiver_name, Account_receiver_id, Sent_Currency, Sent_Amount, Datetime) VALUES (?, ?, ?, ?, ?, ?, ?)
''', transactions)

# Подтверждение изменений
conn.commit()

# Закрытие соединения
conn.close()

print("Данные успешно добавлены в базу данных.")
