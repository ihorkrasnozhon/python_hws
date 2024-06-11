import argparse
import logging
import os
import zipfile
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler

import pandas as pd
import requests


#1. Set up new file logger
def method1(log_file_path):
    # ну тут просто конфиг логгера
    logging.basicConfig(
        # все что дебаг и віше по уровню топсть там инфо ерр варн крит будут логироваться
        level=logging.DEBUG,  # Уровень логирования
        # формат лога что там дата время имя дир уровень лога и настраиваемое сообщение
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            #это чоб не забивало мне память и была только одна копия логгера
            RotatingFileHandler(log_file_path, mode='w', backupCount=1),
            logging.FileHandler(log_file_path),  #ля записи в файл
            logging.StreamHandler()  #для вывода в консоль
        ]
    )

# 2. Еxplore the data provider site and download a csv file with 5k user accounts
def method2345(destination_folder, filename='output', gender=None, num_rows=None):
    response = requests.get("https://randomuser.me/api/?results=20&format=csv")

    if response.status_code == 200:

        logger.info("Downloading data")

        # формируем путь для новго файла по путь+имя
        downloaded_file = os.path.join(destination_folder, f"{filename}_downloaded.csv")
        with open(downloaded_file, 'wb') as file:
            # отут именно записуется
            file.write(response.content)
        logger.info("Data downloaded and saved in %s", downloaded_file)

        # Загружаем данные из файла в новый датафрейм для дальшей фильтрации
        df = pd.read_csv(downloaded_file)

        logger.info("Filtring data")

        # Применяем фильтрацию, если указаны параметры
        if gender:
            # тут датафрейм переопределяется чтоб остались только нужные гендеры
            df = df[df['gender'] == gender]
        if num_rows:
            # а тут просто забирается с головы дфа нужное количество рядков
            df = df.head(int(num_rows))



            logger.info("Editing time")

            # Функция для разбора временного смещения
        def parse_timezone_offset(offset_str):
                # Разделение строки смещения на часы и минуты
            hours, minutes = offset_str.split(':')
                # Преобразование часов и минут в целые числа
            hours = int(hours)
            minutes = int(minutes)
                # Возвращаем timedelta с учетом смещения
            return timedelta(hours=hours, minutes=minutes)

            # мое время
        my_time = datetime.now()
        # +0 время
        current_time = my_time - timedelta(hours=2)
        # апплай автоматически передает как параметр оффсет
        df['current_time'] = current_time + df['location.timezone.offset'].apply(parse_timezone_offset)

        # Изменение содержимого поля name.title
        df['name.title'] = df['name.title'].replace({
            'Mrs': 'missis',
            'Ms': 'miss',
            'Mr': 'mister',
            'Madame': 'mademoiselle'
        })

        # просто переформатирование
        df['dob.date'] = pd.to_datetime(df['dob.date']).dt.strftime('%m/%d/%Y')

        # Преобразование register.date в нужный формат
        df['registered.date'] = pd.to_datetime(df['registered.date']).dt.strftime('%m-%d-%Y, %H:%M:%S')

        # пределяем путь для отфильтррованого файла
        filtered_file = os.path.join(destination_folder, f"{filename}_filtered.csv")
        # тут уже датафрейм в цсв форматируется
        df.to_csv(filtered_file)
        logger.info("Filtered data saved in %s", filtered_file)
    else:
        logger.error("Can't download data: %s", response.status_code)
        exit(1)


    return df


def method9_10_12(destination_folder, df):
    logging.info("Decade dirs generating")
    # Приводим destination_folder к строковому типу потомучто там біл варн в ос пас джоин
    destination_folder = str(destination_folder)
    # Создаем подпапки для каждой декады
    for decade in range(1960, 2021, 10):
        decade_folder = os.path.join(destination_folder, str(decade) + "s")
        os.makedirs(decade_folder, exist_ok=True)

        # Получаем страны из данных для текущего десятилетия
        countries = df[df['dob.date'].between(f"{decade}-01-01", f"{decade+9}-12-31")]['location.country'].unique()

        # Создаем подпапки для каждой страны внутри текущего десятилетия
        for country in countries:
            country_folder = os.path.join(decade_folder, country)
            os.makedirs(country_folder, exist_ok=True)

    # Распределяем пользователей по папкам в соответствии с их датой рождения и страной
    for index, row in df.iterrows():
        dob_year = pd.to_datetime(row['dob.date']).year

        decade = dob_year // 10 * 10
        #subtask 12
        if decade >= 1960:
            country = row['location.country']

            # Определяем путь для папки пользователя
            user_folder = os.path.join(destination_folder, str(decade) + "s", country)

            # Убеждаемся, что папка существует
            os.makedirs(user_folder, exist_ok=True)

            # Сохраняем данные пользователя в файл в соответствующую папку
            filename = f"user_{index}.csv"
            filepath = os.path.join(user_folder, filename)
            row.to_csv(filepath, index=False)

    logging.info("Decade dirs generated")





# левел для итерирования по папкам
def method13(path, level=0):
# для каждого айтема которій есть в списке файлов в директории
    for item in os.listdir(path):
        # єто чтоб проверить что єто папка или файл
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            # итем єто или папка или файл
            logger.info("%s[%s] (папка)", "\t" * level, item)
            method13(item_path, level + 1)
        else:
            logger.info("%s[%s] (файл)", "\t" * level, item)





# для 6
def create_and_change_directory(destination_folder):
        os.makedirs(destination_folder)
        logger.info("Destination dir wasnt exist and was created")



def archive_destination_folder(destination_folder):
    logging.info("Archiving started")
    # Получаем путь к корневой папке
    root_folder = os.path.dirname(destination_folder)
    # Создаем архивный файл в корневой папке под переменной zipf
    with zipfile.ZipFile(os.path.join(str(root_folder), "archive.zip"), 'w') as zipf:
        # Рекурсивно проходимся по всем файлам и подпапкам в папке назначения
        for folder_name, subfolders, filenames in os.walk(str(destination_folder)):
            # Добавляем каждый файл в архив
            for filename in filenames:
                file_path = os.path.join(folder_name, filename)
                # Добавляем файл в архив с относительным от корневого директории путем
                zipf.write(file_path, os.path.relpath(file_path, str(destination_folder)))
    logging.info("Archiving finished")





# пример запуска через парсер
# python hw3-SOLO.py "C:\\Users\\1456112\\PycharmProjects\\python_hws\\hw3\\copy"

def main():
    parser = argparse.ArgumentParser(description="Script description")
    parser.add_argument("destination_folder", type=str, help="Path to the destination folder")
    parser.add_argument("--filename", type=str, default="output", help="Output filename prefix")
    parser.add_argument("--gender", type=str, help="Filter data by gender")
    parser.add_argument("--num_rows", type=int, help="Number of rows to filter")


if __name__ == "__main__":
        log_file_path = 'my_log_file.log'
        method1(log_file_path)
        logger = logging.getLogger()
        # C:\Users\1456112\PycharmProjects\python_hws\hw3
        # destination_folder = input("Enter destination folder path: ")

        # destination_folder = "C:\\Users\\1456112\\PycharmProjects\\python_hws\\hw3"


        # 6th subtask
        destination_folder = "C:\\Users\\1456112\\PycharmProjects\\python_hws\\hw3\\copy"

        if not os.path.exists(destination_folder):
            create_and_change_directory(destination_folder)
            #changedir в нужную папку
        os.chdir(destination_folder)

        filename = input("Enter filename (default: output): ") or "output"
        gender = input("Enter gender to filter data by (male / female): ")
        num_rows = input("Enter number of rows to filter by (optional): ")

        df = method2345(destination_folder, filename, gender, num_rows,)
        method9_10_12(destination_folder, df)
        # 11 я чтото не понял что там надо сортировать

        logging.info("Structure: ")
        logging.info(" ")
        method13(destination_folder)
        logging.info(" ")

        archive_destination_folder(destination_folder)

