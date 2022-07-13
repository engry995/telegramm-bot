from telebot.types import Message
import json
from typing import List
from loader import bot
from database.command import get_last
from states.user_states import UserState
from datetime import datetime, date, timedelta


def get_user_data(user_id) -> dict:
    """
    Получение текущих данных пользователя из состояния пользователя.
    Если состояние еще не инициировано, то берется последний запрос из базы данных.
    Если пользователь новый и данных нет, то состояние заполняется первоначальными данными.
    :param user_id: user ID
    :return: словарь текущего состояния
        Пример:
        data['city'] = 'Париж, Франция'  # Текстовое наименование локации
        data['city_id'] = '504261'  # ID текущей локации
        data['check_in'] = date.today()  # Дата заезда
        data['check_out'] = date.today() + timedelta(1)  # Дата выезда
        data['number_hotels'] = 10  # количество отелей для вывода
        data['foto'] = False  # вывод фото
    """

    try:
        with bot.retrieve_data(user_id) as data:
            res = data
            if not res:
                raise KeyError
    except KeyError:
        record = get_last(user_id)
        bot.set_state(user_id, UserState.all)
        if record:
            record = record[0]
            with bot.retrieve_data(user_id) as data:
                data['city'] = record[2]  # Текстовое наименование локации
                data['city_id'] = record[1]  # ID текущей локации
                check_in = datetime.strptime(record[3], '%Y-%m-%d').date()
                if check_in < date.today():
                    data['check_in'] = date.today()  # Дата заезда
                    data['check_out'] = date.today() + timedelta(1)  # Дата выезда
                else:
                    data['check_in'] = check_in  # Дата заезда
                    data['check_out'] = datetime.strptime(record[4], '%Y-%m-%d').date()
                data['number_hotels'] = 5  # количество отелей для вывода
                data['foto'] = 0  # количество фото
        else:
            # Если данных в базе нет, заполняем данными по умолчанию
            with bot.retrieve_data(user_id) as data:
                data['city'] = 'Париж, Франция'  # Текстовое наименование локации
                data['city_id'] = '504261'  # ID текущей локации
                data['check_in'] = date.today()  # Дата заезда
                data['check_out'] = date.today() + timedelta(1)  # Дата выезда
                data['number_hotels'] = 5  # количество отелей для вывода
                data['foto'] = 0  # количество фото

        with bot.retrieve_data(user_id) as data:
            res = data
    return res


def listener(message: List[Message], js: bool = False) -> None:
    """
    Функция для отладки, при работе не используется.
    Выводит все сообщения пользователей на экран.
    :param message: Сообщение из телеграм.
    :param js: Ключ вывода json сообщения.
    :return: None
    """

    if message:
        message = message[0]
        print(f'Сообщение id={message.id} от {message.from_user.full_name}, user_id={message.from_user.id}: {message.text}')
        if js:
            print(json.dumps(message.json, indent=4, ensure_ascii=False))
    else:
        print('Получен пустой список.')
