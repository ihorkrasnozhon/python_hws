import argparse
import logging
import os
import requests
import shutil
from datetime import datetime
import pandas as pd




# ЧТОБ НАЧАТЬ ПРОЦЕСС НАДО ВБИТЬ В ШЕЛЛ ИЛИ ТЕРИМНАЛ ИДЕШКИ%:
# python data_processor.py --destination C:\Users\1456112\PycharmProjects\python_hws\hw3\output --filename user_data --gender female --rows 1000 INFO
# python [ИМЯ ФАЙЛА] --destination ПУТЬ ДО ФАЙЛА --filename ИМЯ СОЗДАВАЕМОГО ФАЙЛА --gender female ЄТО ФИЛЬТР --rows ЄТО КОЛИЧЕСТВО РЯДКОВ УРОВЕНЬ ЛОГИРОВНИЯ



# URL для скачивания данных
DATA_URL = "https://randomuser.me/api/?results=5000&format=csv"

# Настройка логирования
logger = logging.getLogger(__name__)


def setup_logger(log_level):
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(log_level)


def download_data(filename):
    logger.info("Скачивание данных...")
    response = requests.get(DATA_URL)
    if response.status_code == 200:
        if os.path.dirname(filename):
            os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'wb') as f:
            f.write(response.content)
        logger.info("Данные скачаны и сохранены в %s", filename)
    else:
        logger.error("Не удалось скачать данные. Статус-код: %s", response.status_code)
        exit(1)


def read_and_filter_data(filename, gender=None, rows=None):
    logger.info("Чтение и фильтрация данных...")
    df = pd.read_csv(filename)
    if gender:
        df = df[df['gender'] == gender]
    if rows:
        df = df.head(rows)
    return df


def process_data(df):
    logger.info("Обработка данных...")
    df['global_index'] = df.index
    df['current_time'] = df.apply(lambda x: datetime.now(), axis=1)
    df['name.title'] = df['name.title'].replace(
        {"Mrs": "missis", "Ms": "miss", "Mr": "mister", "Madame": "mademoiselle"}
    )
    df['dob.date'] = pd.to_datetime(df['dob.date']).dt.strftime('%m/%d/%Y')
    df['registered.date'] = pd.to_datetime(df['registered.date']).dt.strftime('%m-%d-%Y, %H:%M:%S')
    return df


def create_folder_structure(base_path, data):
    logger.info("Создание структуры папок...")
    os.makedirs(base_path, exist_ok=True)

    grouped = data.groupby([data['dob.date'].str[-4:].astype(int) // 10 * 10, 'location.country'])

    for (decade, country), group in grouped:
        if decade < 1960:
            continue
        decade_folder = os.path.join(base_path, f"{decade}-th")
        country_folder = os.path.join(decade_folder, country)
        os.makedirs(country_folder, exist_ok=True)

        max_age = 2023 - int(group['dob.date'].str[-4:].max())
        group['registered.date'] = pd.to_datetime(group['registered.date'], format='%m-%d-%Y, %H:%M:%S',
                                                  errors='coerce')

        avg_registered_years = group['registered.date'].apply(lambda x: 2023 - x.year if pd.notnull(x) else 0).mean()

        common_id_name_series = group['id.name'].mode()
        common_id_name = common_id_name_series[0] if not common_id_name_series.empty else 'unknown'

        filename = f"max_age_{max_age}_avg_registered_{avg_registered_years:.1f}_popular_id_{common_id_name}.csv"
        filepath = os.path.join(country_folder, filename)

        group.to_csv(filepath, index=False, sep=';')

        logger.info("Создан файл: %s", filepath)


def log_folder_structure(path, level=0):
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            logger.info("%s[%s] (папка)", "\t" * level, item)
            log_folder_structure(item_path, level + 1)
        else:
            logger.info("%s[%s] (файл)", "\t" * level, item)


def archive_folder(src_path, zip_path):
    logger.info("Архивирование папки...")

    # Получаем абсолютный путь к архиву
    abs_src_path = os.path.abspath(src_path)
    abs_zip_path = os.path.abspath(zip_path)

    # Убеждаемся, что архив создается вне архивируемой папки
    if abs_src_path.startswith(abs_zip_path):
        logger.error("Архив не может быть создан внутри архивируемой папки.")
        exit(1)

    shutil.make_archive(zip_path, 'zip', src_path)
    logger.info("Папка заархивирована в %s.zip", zip_path)


def main():
    parser = argparse.ArgumentParser(description='Обработка и архивация пользовательских данных.')
    parser.add_argument('--destination', required=True, help='Папка назначения')
    parser.add_argument('--filename', default='output', help='Имя выходного файла')
    parser.add_argument('--gender', choices=['male', 'female'], help='Фильтрация по полу')
    parser.add_argument('--rows', type=int, help='Количество строк для обработки',
                        default=100)  # Ограничиваем количество строк до 100
    parser.add_argument('log_level', nargs='?', default='INFO', help='Уровень логирования')

    args = parser.parse_args()

    setup_logger(args.log_level.upper())

    # Скачивание данных
    csv_filename = f"{args.filename}.csv"
    download_data(csv_filename)

    # Чтение и фильтрация данных
    df = read_and_filter_data(csv_filename, args.gender, args.rows)

    # Обработка данных
    df = process_data(df)

    # Создание структуры папок и сохранение файлов
    create_folder_structure(args.destination, df)

    # Логирование структуры папок
    log_folder_structure(args.destination)

    # Архивирование папки
    archive_path = os.path.join(os.path.dirname(args.destination), args.filename)
    archive_folder(args.destination, archive_path)

    # Сообщение о завершении архивирования
    logger.info("Архивирование завершено. Программа завершена.")


if __name__ == '__main__':
    main()
