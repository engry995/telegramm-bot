import requests.exceptions
import urllib3.exceptions
from loader import bot
from telebot.types import Message, InputMediaPhoto
import telebot.apihelper
from utils.api_hotels import get_hotels, get_photo
from handlers.custom_heandlers.related import step
from utils.utils import get_user_data
from database.command import save_request_to_db

"""
Здесь определены базовые команды бота.
"""


def handler_command(user_id: int, command: str = '/lowprice') -> None:
    """
    Обработчик запроса пользователя.
    - определяется режим сортировки, запрашиваются отели по текущим данным пользователя.
    - вызывается функция отправки сообщений с отелями пользователю
    - запрос сохраняется в базу данных.
    :param user_id: ID пользователя.
    :param command: обрабатываемая команда.
    :return: None
    """

    bot.send_message(user_id, 'Получаем информацию...')

    sort, sort_to_db = 'PRICE', 'P'
    if command == '/highprice':
        sort, sort_to_db = 'PRICE_HIGHEST_FIRST', 'PHF'
    elif command == '/bestdeal':
        sort, sort_to_db = 'DISTANCE_FROM_LANDMARK', 'DFL'

    data = get_user_data(user_id)
    hotels = get_hotels(data, sortOrder=sort)
    send_hotels(hotels, user_id, data['foto'])
    save_request_to_db(hotels, user_id, sort_to_db, **data)
    step(user_id, 2)


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def comm(message: Message) -> None:
    command = message.text
    handler_command(message.from_user.id, command=command)


def send_hotels(hotels: list, user_id: int, number_foto: int = False) -> None:
    """
    Отправка данных об отелях пользователю.
    :param hotels: список словарей с данными об отелях
    :param user_id: ID пользователя
    :param number_foto: количество выводимых фото, 0 или False - фото не выводятся
    :return: None
    """
    for hotel in hotels:
        text = f"<b>{hotel['name']}</b>\n" \
               f"<i>{hotel['address']}</i>\n" \
               f"{hotel['price']}\n" \
               f"{hotel['url']}"
        if number_foto:
            foto = get_photo(hotel['id'])
            for _ in range(3):
                # выполняются три попытки отправить медиагруппу с фото, каждый раз с новым набором фото
                foto_list = [InputMediaPhoto(next(foto)) for _ in range(number_foto - 1)]
                # к последнему фото добавляем подпись
                foto_list.append(InputMediaPhoto(next(foto), caption=text, parse_mode='HTML'))
                try:
                    bot.send_media_group(user_id, foto_list)
                    break
                except [telebot.apihelper.ApiTelegramException, urllib3.exceptions.ReadTimeoutError] as msg:
                    print('Ошибка отправки медиагруппы. ID отеля:', hotel['id'], msg)
            else:
                text = 'Фото получить не удалось.\n\n' + text
                bot.send_message(user_id, text,
                                 parse_mode='HTML',
                                 disable_web_page_preview=True,
                                 )
        else:
            bot.send_message(user_id, text,
                             parse_mode='HTML',
                             disable_web_page_preview=True,
                             )
