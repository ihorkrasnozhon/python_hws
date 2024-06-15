import csv
import logging
import sqlite3
import re
from datetime import datetime
from functools import wraps
from logging.handlers import RotatingFileHandler


import requests

log_file_path = 'api_log_file.log'
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(log_file_path, mode='w', backupCount=1),
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger()


# декоратор для бдшки чтоб дикорировать функции и давать
# им возможность редактировать бд ии иметь с ней связь
def db_connection(func):
    # рап чтоб декоратор не менял атрибуті декорируемой функции на свои
    @wraps(func)
    # коннтекстный менеджер виз чтоб корректно открывать закрывать и взаимодействовать с ресурсом
    # и передаем кортеж аргументов и в виде словаря кейворд агрументы функции
    def with_connection(*args, **kwargs):
        conn = sqlite3.connect('bank.db')
        try:
            # декорируемая фунция вызывается с переданными значениями и доступом к бд чтоб изменять ее
            result = func(conn, *args, **kwargs)
            conn.commit()

            # если возникают исключения то бд роллбекается до предыдущей версии
        except Exception as e:
            conn.rollback()
            logger.error(f"Error: {str(e)}")
            result = {"status": "failure", "message": str(e)}
        finally:
            # если функция успещно или неуспещно то конн все равно закрывается
            conn.close()
        return result
    return with_connection

#alidation for user_full_name field which divide it for name and surname by any kind of spaces and filter out all non-alphabetical symbols
# сплитит имяфамилию один раз на имя фамилию и удаляет всякую фигню
def split_user_name_surname(user_full_name):
    # Удаляем начальные и конечные пробелы
    user_full_name = user_full_name.strip()
    # Разбиваем на имя и фамилию по первому пробелу
    name, surname = user_full_name.split(maxsplit=1)
    # отделяем ненужніе символі из имени и фамилии а потом обратно собираем в одно знаечние
    name = ''.join(filter(str.isalpha, name))
    surname = ''.join(filter(str.isalpha, surname))
    return name, surname




#Set of functions which can add user/bank/account to the DB.

# функция для ддобавления юзера в бд
@db_connection
def add_user(conn, *users):
    # logging.info(users)
    cursor = conn.cursor()
    # для каждого юзера достается его информация из словаря
    for user in users:
        name, surname = split_user_name_surname(user['user_full_name'])
        name = name.strip()
        surname = surname.strip()
        logging.info(name)
        logging.info(surname)
        # валидация имени перед добавлением в базу данных
        validate_field_value(name, 'name')
        # валидация фамилии перед добавлением в базу данных
        validate_field_value(surname, 'surname')
        accounts = user.get('accounts', '')
        birth_day = user.get('birth_day', '')
        try:
            # потом курсор выполняет скл запрос для добавления нового юера
            cursor.execute('INSERT INTO User (name, surname, birth_day, accounts) VALUES (?, ?, ?, ?)',
                           (name, surname, birth_day, accounts))
        # если есть какаято ошибка целостности то мы ее ловим
        except sqlite3.IntegrityError as e:
            logger.error(f"Error: {str(e)}")
            return {"status": "failure", "message": str(e)}
    return {"status": "success", "message": "User(s) added successfully"}



# тут тоже декоратор туда сюда добавление новії банков в бд
@db_connection
def add_bank(conn, *banks):
    logging.info("Adding new bank.")
    logging.info(banks)
    cursor = conn.cursor()
    for bank in banks:
        try:
            cursor.execute('INSERT INTO Bank (name, capital) VALUES (?, ?)', (bank['name'], bank['capital']))
        except sqlite3.IntegrityError as e:
            logger.error(f"Error: {str(e)}")
            return {"status": "failure", "message": str(e)}
    conn.commit()
    return {"status": "success", "message": "Bank(s) added successfully"}


# тут функция для ото аккаунтов новіх
@db_connection
def add_account(conn, *accounts):
    cursor = conn.cursor()
    logging.info(accounts)

    for account in accounts:
        logging.info(account['status'])
        validate_field_value(account['status'], 'status')
        try:
            cursor.execute('''
                INSERT INTO Account (user_id, type, account_number, bank_id, bank_name, currency, balance, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (account['user_id'], account['type'], account['account_number'], account['bank_id'], account['bank_name'],
                  account['currency'], account['balance'], account['status']))
            conn.commit()
        except sqlite3.IntegrityError as e:
            logging.error(f"Error: {str(e)}")
            return {"status": "failure", "message": str(e)}
    return {"status": "success", "message": "Account(s) added successfully"}




#Set of functions which can add the same data about user||bank||account from csv file.


# file_path = "C:\\Users\\1456112\\PycharmProjects\\python_hws\\hw4\\add_users.csv"
# функция для добавления нформации про юзеров с цсв файла в бдшку
@db_connection
def add_users_from_csv(conn, file_path):
    cursor = conn.cursor()
    try:
        # открыть в режиме читания файл по пути и опредедлить это в переменную файл
        with open(file_path, mode='r') as file:
            # создаем обект метода для итераций по файлу
            reader = csv.DictReader(file)
            # оно читает файл и выполняет запросы для каждой строчки
            for row in reader:
                name, surname = split_user_name_surname(row['user_full_name'])
                cursor.execute('INSERT INTO User (name, surname, birth_day, accounts) VALUES (?, ?, ?, ?)',
                               (name, surname, row['birth_day'], row['accounts']))
        logging.info("Adding from CSV completed")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"status": "failure", "message": str(e)}
    return {"status": "success", "message": "Users added from CSV successfully"}


#про юанки с цсв файла в бд
@db_connection
def add_banks_from_csv(conn, file_path):
    cursor = conn.cursor()
    try:
        with open(file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                cursor.execute('INSERT INTO Bank (name, capital) VALUES (?, ?)', (row['name'], row['capital']))
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"status": "failure", "message": str(e)}
    return {"status": "success", "message": "Banks added from CSV successfully"}


# то же с акааунтами
@db_connection
def add_accounts_from_csv(conn, file_path):
    cursor = conn.cursor()
    try:
        with open(file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                validate_account_number(row['account_number'])
                cursor.execute('''
                    INSERT INTO Account (user_id, type, account_number, bank_id, bank_name, currency, amount, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (row['user_id'], row['type'], row['account_number'], row['bank_id'], row['bank_name'],
                      row['currency'], row['amount'], row['status']))
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"status": "failure", "message": str(e)}
    return {"status": "success", "message": "Accounts added from CSV successfully"}



#Set of functions which can modify one particular user/bank/account row of data


# для модификации юзера
@db_connection
def modify_user(conn, user_id, **kwargs):
    cursor = conn.cursor()

    # обєденяем все кварги в строку с полями, разделяя их комой с пробелом
    #                   перебираем все ключи словаря
    fields = ', '.join(f"{k} = ?" for k in kwargs.keys())
    # создаем новій списк с переданніми значениями єтих полей
    values = list(kwargs.values())
    # logging.info(kwargs.get('name',''))

    #и добавляем в конец ид целевого юзера заместь "?" снизу
    values.append(user_id)
    validate_field_value(kwargs.get('name', ''),  'name')
    validate_field_value(kwargs.get('surname', ''),  'surname')

    # формируем строчку запроса на измененияе данніх
    query = f"UPDATE User SET {fields} WHERE id = ?"
    try:
        # ну и віполняем запрос с нужніми данніми
        cursor.execute(query, values)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"status": "failure", "message": str(e)}
    return {"status": "success", "message": "User modified successfully"}

# модифицируем информацию про банк ну и делаем по сути то же самое что и с юзерами
@db_connection
def modify_bank(conn, bank_id, **kwargs):
    logging.info(kwargs)
    cursor = conn.cursor()
    fields = ', '.join(f"{k} = ?" for k in kwargs.keys())
    values = list(kwargs.values())
    values.append(bank_id)
    query = f"UPDATE Bank SET {fields} WHERE id = ?"
    try:
        cursor.execute(query, values)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"status": "failure", "message": str(e)}
    return {"status": "success", "message": "Bank modified successfully"}

# ну и с аккаунтами
@db_connection
def modify_account(conn, id, **kwargs):
    logging.info("Account is being modified.")
    cursor = conn.cursor()
    # Выполняем запрос к базе данных, чтобы получить текущее значение account_number
    cursor.execute("SELECT account_number FROM Account WHERE id = ?", (id,))
    current_account_number = cursor.fetchone()[0]  # Получаем текущее значение account_number
    fields = ', '.join(f"{k} = ?" for k in kwargs.keys())
    values = list(kwargs.values())
    # for key, value in kwargs.items():
    #     logging.info(f"Key: {key}, Value: {value}")
    values.append(id)
    # logging.info(user_id)
    # logging.info(f"Account number: {current_account_number}")
    validate_account_number(current_account_number)  # Проверяем текущее значение account_number
    query = f"UPDATE Account SET {fields} WHERE id = ?"
    try:
        cursor.execute(query, values)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"status": "failure", "message": str(e)}
    return {"status": "success", "message": "Account modified successfully"}




# Set of functions which can delete one particular user/bank/account row


# удаление юзера
@db_connection
def delete_user(conn, id):
    cursor = conn.cursor()
    try:
        # тут ваще функция простейшая
        logging.info("User is being deleetd...")
        cursor.execute("DELETE FROM User WHERE id = ?", (id,))
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"status": "failure", "message": str(e)}
    return {"status": "success", "message": "User deleted successfully"}

# тоже удадление ьанка
@db_connection
def delete_bank(conn, bank_id):
    logging.info("Deleting bank.")
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Bank WHERE id = ?", (bank_id,))
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"status": "failure", "message": str(e)}
    return {"status": "success", "message": "Bank deleted successfully"}

@db_connection
def delete_account(conn, account_id):
    cursor = conn.cursor()
    try:
        # ну и ужаление аккаунта
        cursor.execute("DELETE FROM Account WHERE id = ?", (account_id,))
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"status": "failure", "message": str(e)}
    return {"status": "success", "message": "Account deleted successfully"}



# Set of functions which performs money transfer from one card to another.

# обменній курс типа
def get_exchange_rate(currency_from, currency_to):
    # тут я зарегался и ключик получил

    api_key = 'fca_live_Lb2Lhvi11nkq6E2337YHhW613CvLzCgNsonteTY8'
    url = f"https://api.freecurrencyapi.com/v1/latest?apikey={api_key}&currencies={currency_to}&base_currency={currency_from}"
    response = requests.get(url)
    if response.status_code == 200:
        rates = response.json().get('data', {})
        # если не удалось получить курс целевой валюті для отправной, то будет равняться 1.0
        return rates.get(currency_to, 1.0)
    else:
        logger.error(f"Error fetching exchange rate: {response.status_code}")
        return None


# function which performs money transfer from one card to another
@db_connection
def transfer_money(conn, sender_account_id, receiver_account_id, amount):
    cursor = conn.cursor()

    # вібираем всю информацию про аккаунт юзера с нужнім ид
    cursor.execute("SELECT * FROM Account WHERE id = ?", (sender_account_id,))
    # как аккаунт отправителя мі получаем первую строчку респонса
    sender_account = cursor.fetchone()
    # logging.info(sender_account)

    # тут получаем информацию про получателя
    cursor.execute("SELECT * FROM Account WHERE id = ?", (receiver_account_id,))
    receiver_account = cursor.fetchone()
    # logging.info(receiver_account)

    # єто если указались неправильній айдишники например и не нашлись акаунт/і
    if not sender_account or not receiver_account:
        return {"status": "failure", "message": "One or both accounts not found"}

    #  6       amount REAL NOT NULL,
    sender_balance = sender_account[7]
    # logging.info(sender_balance)

    #  5       currency TEXT NOT NULL,
    sender_currency = sender_account[6]

    #  5       currency TEXT NOT NULL,
    receiver_currency = receiver_account[6]

#если денюжки нема
    if float(sender_balance) < amount:
        return {"status": "failure", "message": "Insufficient funds"}

    # logging.info(sender_account[8])
    logging.info("Validating sender account:")
    validate_field_value(sender_account[8], 'status')
    logging.info("Validating receiver account:")

    validate_field_value(receiver_account[8], 'status')

# по дефолту предполагается что валюта отправителя равна валбте получателя
    exchange_rate = 1
    # но если нет то переопределяется просто с візовом функции ввіше
    if sender_currency != receiver_currency:
        exchange_rate = get_exchange_rate(sender_currency, receiver_currency)
        if exchange_rate is None:
            return {"status": "failure", "message": "Error fetching exchange rate"}

# ну тут понятно что для получателя будет вот так меняться
    converted_amount = amount * exchange_rate

    # logging.info("converted_amount")
    # logging.info(converted_amount)
    # произведение транзации, изменение +- баланса
    try:
        # ИЗМЕНИЛ АМАУНТ НА БАЛАНС
        cursor.execute("UPDATE Account SET balance = balance - ? WHERE id = ?", (amount, sender_account_id))
        cursor.execute("UPDATE Account SET balance = balance + ? WHERE id = ?", (converted_amount, receiver_account_id))
        logging.info("Transaktion sucseeded")
        #вот тут ругалось на то что склайт3 четотам старый и не поддерживает чето там с дейттаймом пришлось изменить
        transaktion_datetime = datetime.now()
        transaktion_datetime = validate_transaction_datetime(transaktion_datetime)
        formatted_datetime = transaktion_datetime.strftime("%Y-%m-%d %H:%M:%S")
        # добавляем запись в таблицу транзайкий
        cursor.execute('''
            INSERT INTO "Transaction" (Bank_sender_name, Account_sender_id, Bank_receiver_name, Account_receiver_id, Sent_Currency, Sent_Amount, Datetime)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (sender_account[5], sender_account_id, receiver_account[5], receiver_account_id, sender_currency, amount, formatted_datetime))

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"status": "failure", "message": str(e)}

    return {"status": "success", "message": "Money transferred successfully"}


# validations

# Validate fields with strict set of values mentioned in db scheme
def validate_field_value(value, field_name):
    logging.info(f"Validating {field_name}: {value}")
    if field_name == 'name':
        if not value.isalpha():
            raise ValueError(
                f"Invalid value '{value}' for field '{field_name}'! Only alphabetical characters are allowed.")
        if len(value) > 50:
            raise ValueError(f"Invalid value '{value}' for field '{field_name}'! Maximum length is 50 characters.")
    elif field_name == 'surname':
        if not value.isalpha():
            raise ValueError(
                f"Invalid value '{value}' for field '{field_name}'! Only alphabetical characters are allowed.")
        if len(value) > 50:
            raise ValueError(f"Invalid value '{value}' for field '{field_name}'! Maximum length is 50 characters.")
    elif field_name == 'age':
        # Проверка возраста
        try:
            age = int(value)
            if age < 18 or age > 100:
                raise ValueError(f"Invalid value '{value}' for field '{field_name}'! Age must be between 18 and 100.")
        except ValueError:
            raise ValueError(f"Invalid value '{value}' for field '{field_name}'! Age must be an integer.")
    elif field_name == 'status':
        # Проверка типа аккаунта
        allowed_types = ['gold', 'silver', 'platinum']  # Допустимые типы аккаунтов
        if value not in allowed_types:
            raise ValueError(
                f"Invalid value '{value}' for field '{field_name}'! Allowed types are {', '.join(allowed_types)}.")
    else:
        raise ValueError(f"Validation not implemented for field '{field_name}'!")

    logging.info("Validated OK")


#If datetime of transaction wasn’t passed, put the current time.
def validate_transaction_datetime(transaction_datetime):
    # logging.info("datetime")

    if not transaction_datetime:
        return datetime.utcnow()
    else:
        return transaction_datetime

# Validation for account number
def validate_account_number(account_number):
    # If it contains one of #%_?& just replace them with dash.
    account_number = re.sub(r'[#%_?&]', '-', account_number)
    # it should be string of 18 chars (raise an error: too little/many chars! depend on amount)
    # logging.info(account_number)
    if len(account_number) < 18:
        raise ValueError("Too few chars. Must be a string of 18.")
    if len(account_number) > 18:
        raise ValueError("Too many chars. Must be a string of 18.")
    # начинается ли с ИД-- и соответствует ли нужному формату
    #from 1 to 3 letters
    #then one dash
    #then any amount of digits but at least one
    #then one dash.

    # короче я изменил паттерн потомучто он чето не рабочий был
    if not re.match(r'^ID--[a-zA-Z]{3}-\d{6}-[a-zA-Z]{3}$', account_number):
        raise ValueError("Account number has wrong format!")
    return account_number






def get_bank_input():
    banks = []
    while True:
        bank_name = input("Enter bank name (or 'done' to finish): ")
        if bank_name.lower() == 'done':
            break
        try:
            bank_capital = float(input(f"Enter capital for {bank_name}: "))
        except ValueError:
            print("Invalid capital amount. Please enter a valid number.")
            continue
        banks.append({'name': bank_name, 'capital': bank_capital})
    return banks

def get_account_modification_input():
    print("Available fields for modification:")
    available_fields = ['user_id', 'type', 'account_number', 'bank_id', 'bank_name', 'currency', 'amount', 'status']
    for field in available_fields:
        print(f"- {field}")

    account_id = input("Enter the account ID to modify: ").strip()
    modifications = {}

    while True:
        field = input("Enter the field to modify (or 'done' to finish): ").strip().lower()
        if field == 'done':
            break
        value = input(f"Enter the new value for {field}: ").strip()
        modifications[field] = value
    return account_id, modifications

def send_money():
    sender_account_id = input("Enter sender's account ID: ")
    receiver_account_id = input("Enter receiver's account ID: ")
    amount = float(input("Enter the amount to transfer: "))
    return sender_account_id, receiver_account_id, amount


# ----------------------ТАСК 3-----------------------------


# Bank which operates the biggest capital.
@db_connection
def bank_with_largest_capital(conn):
    cursor = conn.cursor()
    logging.info("Searching for the richest bank")
    # фильтруем банки по спаданию капитала и берем самый первый
    query = """
        SELECT name
        FROM Bank
        ORDER BY capital DESC
        LIMIT 1
    """
    # выполняем запрос
    cursor.execute(query)
    # возвращает один жлемент с индексом 0
    return cursor.fetchone()[0]

@db_connection
def get_bank_name_of_old_user(conn):
    cursor = conn.cursor()

    # Получаем аккаунт старого пользователя из таблицы User
    cursor.execute("SELECT accounts FROM User ORDER BY birth_day ASC LIMIT 1")
    # извлекаем только одну строчку
    user_account = cursor.fetchone()
    # logging.info(user_account[0])

    if not user_account:
        logging.error("Cannot find user`s accounts")
        return None

    # Получаем информацию о банке из таблицы Account
    cursor.execute("SELECT bank_name FROM Account WHERE id = ?", (user_account[0],))
    bank_name = cursor.fetchone()
    # logging.info(bank_name)

    if not bank_name:
        return None  # Аккаунт пользователя не найден или нет информации о банке

    return bank_name[0]  # Возвращаем название банка

@db_connection
def bank_with_most_outbound_transactions(conn):
    cursor = conn.cursor()

    # Находим банк с наибольшим количеством уникальных транзакций
    query = """
        SELECT Bank_sender_name, COUNT(*) AS frequency
        FROM "Transaction"
        GROUP BY Bank_sender_name
        ORDER BY frequency DESC
        LIMIT 1;
    """
    cursor.execute(query)
    bank_sender_name = cursor.fetchone()[0]

    return bank_sender_name

@db_connection
def search_users_with_empty_info(conn):
    cursor = conn.cursor()
    # Находим идентификаторы пользователей с пустыми полями.
    query = """
        SELECT id
        FROM User
        WHERE name = '' OR surname = '' OR birth_day = '' OR accounts = ''
    """
    cursor.execute(query)
    users_to_delete = cursor.fetchall()
    logging.info(users_to_delete)
    # Удаляем каждого пользователя с пустыми полями
    for user_id in users_to_delete:
        delete_user(user_id[0])
    # Фиксируем изменения в базе данных.
    conn.commit()
    return {"status": "success", "message": "Users with empty information deleted successfully"}

from datetime import datetime, timedelta

@db_connection
def user_transactions_last_3_months(conn, sender_name):
    cursor = conn.cursor()
    namesurname = split_user_name_surname(sender_name)
    # logging.info(namesurname[0])

    logging.info("Searching for user...")
    query_user_id = """
            SELECT accounts
            FROM User
            WHERE name = ? AND surname = ?
        """
    cursor.execute(query_user_id, (namesurname[0], namesurname[1]))
    user_id = cursor.fetchone()

    if user_id is None:
        logging.error("Failed to find user.")
        return {"status": "failure", "message": f"User '{sender_name}' not found"}

    user_id = user_id[0]
    logging.info(user_id)


    logging.info("Searching for transactions...")

    three_months_ago = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d %H:%M:%S')
    # logging.info(three_months_ago)
    # Запрос для получения транзакций пользователя за последние три месяца
    query_transactions = """
            SELECT *
            FROM "Transaction"
            WHERE Account_sender_id = ? AND Datetime >= ?
        """
    cursor.execute(query_transactions, (user_id, three_months_ago))

    transactions = cursor.fetchall()
    # logging.info(transactions)

    if not transactions:
        return {"status": "success", "message": f"No transactions found for user '{sender_name}' in the last 3 months"}

    # Преобразуем результат в удобный формат (например, список словарей)
    formatted_transactions = []
    for transaction in transactions:
        transaction_dict = {
            "transaction_id": transaction[0],
            "Bank Sender name": transaction[1],
            # "account_sender_id": transaction[2],
            "Bank receiver name": transaction[3],
            # "account receiver id": transaction[4],
            "send currency": transaction[5],
            "send amount": transaction[6],
            "timedate of transaction": transaction[7]
        }
        formatted_transactions.append(transaction_dict)

        print(f"Transaction ID {transaction_dict['transaction_id']} from bank '{transaction_dict['Bank Sender name']}' "
              f"to bank '{transaction_dict['Bank receiver name']}' sent {transaction_dict['send amount']} "
              f"{transaction_dict['send currency']} on {transaction_dict['timedate of transaction']}.")
        logging.info("Search completed.")







if __name__ == "__main__":


    # # РАБОТАЕТ ОФИГЕТЬ и даже в разніе валюти
    # sender_account_id, receiver_account_id, amount = send_money()
    # transfer_money(sender_account_id, receiver_account_id, amount)



    # # Какаято жопа но работает
    # account_id, modifications = get_account_modification_input()
    # # logging.info(account_id)
    # if account_id and modifications:
    #     response = modify_account(id=account_id, **modifications)
    #     print(response)
    # else:
    #     print("No modifications to make.")

    # Работает
    # banks = get_bank_input()
    # if banks:
    #     response = add_bank(*banks)
    #     logging.info(response)
    # else:
    #     print("No banks to add.")

    #Работает
    # add_users_from_csv("C:\\Users\\1456112\\PycharmProjects\\python_hws\\hw4\\add_users.csv")


# чет я подумал и короче будет у меня парт 3 в этом файле тоже

#     Работает
#     print("Bank with largest capital: ", bank_with_largest_capital())

    #     Работает
    # print("Bank with oldest customer: ", get_bank_name_of_old_user())

    #Рбаотет
    # print("Bank with the biggest amount of out transactions: ", bank_with_most_outbound_transactions())

    # Работает
    # print("Report about deletinng: ", search_users_with_empty_info())

    #С хрустиком но работает тоже
    # sender_name = input("Enter user`s full name to check his transactions: ")
    # print("User`s transactions: ")
    # user_transactions_last_3_months(sender_name)

    # add_user({'user_full_name': 'John Deer', 'birth_day': '1990-01-01', 'accounts': '1'})

    pass