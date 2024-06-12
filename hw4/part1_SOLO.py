import logging
import sqlite3


# Настройка логгера
log_file_path = 'create_database.log'
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_database(unique_name_surname):
# коннект с склайт для создания бдшки если она нне существует или просто для вщаимодействия
    logging.info("Connection to DB")
    conn = sqlite3.connect('bank.db')
    # коннектим курсор для запросов и управления бд
    cursor = conn.cursor()

# создаем таблицу багка с типами и именами какие нужны нам
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Bank (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            capital REAL DEFAULT 0.0
        )
    ''')
    logging.info("Banks table created")

    # создаем таблицу транзаций
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
    logging.info("Transaktions table created")

    # юзеров
    user_table_creation_query = '''
        CREATE TABLE IF NOT EXISTS User (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            surname TEXT NOT NULL,
            birth_day TEXT,
            accounts TEXT NOT NULL
        '''
    if unique_name_surname:
        # если уникальное то мы задаем что сочитание имя фамилии должно быть уникальным
        user_table_creation_query += ', UNIQUE (name, surname)'
        logging.info("+UNIQUE")
    user_table_creation_query += ')'
# ну ии курсор завершает создание таблицы
    cursor.execute(user_table_creation_query)
    logging.info("User table created")

    # Indexes
    #  0       id INTEGER PRIMARY KEY AUTOINCREMENT,
    #  1       user_id INTEGER NOT NULL,
    #  2       type TEXT NOT NULL CHECK (type IN ('credit', 'debit')),
    #  3       account_number TEXT NOT NULL UNIQUE,
    #  4       bank_id INTEGER NOT NULL,
    #  5       currency TEXT NOT NULL,
    #  6       amount REAL NOT NULL,
    #  7       status TEXT NOT NULL CHECK (status IN ('gold', 'silver', 'platinum')),
    #         FOREIGN KEY (user_id) REFERENCES User(id),
    #         FOREIGN KEY (bank_id) REFERENCES Bank(id)


#ИЗМЕНИЛ АМАУНТ НА БАЛАНС
    #аккаунті
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Account (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL CHECK (type IN ('credit', 'debit')),
            account_number TEXT NOT NULL UNIQUE,
            bank_id INTEGER NOT NULL,
            bank_name TEXT NOT NULL,
            currency TEXT NOT NULL,
            balance REAL NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('gold', 'silver', 'platinum')),
            FOREIGN KEY (user_id) REFERENCES User(id),
            FOREIGN KEY (bank_id) REFERENCES Bank(id)
        )
    ''')
    logging.info("Accounts table created")

    # сохраняем изменения и закрываем связь с бдкшкйой
    conn.commit()
    conn.close()
    logging.info("closed the connection to bd")

if __name__ == "__main__":
        # вариативность уникальности
    unique_name_surname_input = input("Should name and surname be unique? (yes/no): ").strip().lower()

    if unique_name_surname_input in ['yes', 'y']:
        unique_name_surname = True
    elif unique_name_surname_input in ['no', 'n']:
        unique_name_surname = False
    else:
        print("Invalid input. Please enter 'yes' or 'no'.")
        exit(1)

    create_database(unique_name_surname)
