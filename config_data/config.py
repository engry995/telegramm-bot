"""
Настройки бота, должны храниться в файле .env в корневом каталоге проекта.
COMMANDS - список собственных команд.
"""

import os
from dotenv import load_dotenv, find_dotenv

if not (p := find_dotenv()):
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv(dotenv_path=p)

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')
COMMANDS = (
    ('start', "Запустить бота"),
    ('help', "Вывести справку"),
    ('highprice', 'самые дорогие отели в городе'),
    ('lowprice', 'недорогие отели в городе'),
    ('bestdeal', 'отели подходящие по цене и удалению от центра'),
    ('history', 'история поиска'),
    ('city', 'выбрать город/даты'),
)

NUMBER_OF_FOTO = 7  # количество выводимых фото по умолчанию
DES_TO_FILE = True  # запись запроса уточнения локации в файл
HOTELS_TO_FILE = False  # запись запроса отелей в файл
FOTO_TO_FILE = True  # запись запросов фото в файл
RESPONSE_FROM_FILE = True  # попытка считать ответ из файла, если подходящий есть в базе (только для FOTO и DES)

HISTORY = 5  # Количество запросов выводимых в истории
