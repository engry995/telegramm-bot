from loader import bot
from telebot.types import Message, CallbackQuery
from datetime import datetime, date, timedelta
from database.command import get_history_from_db, get_req_from_db, get_hotel_by_req
from .related import step
from .base import send_hotels
from keyboards.inline import history_keyboard


@bot.message_handler(commands=['history'])
def history_command(message: Message) -> None:
    """
    Функция обработки команды history
    """
    history(message.from_user.id)


def history(user_id: int) -> None:
    """
    Отправка пользователю истории его запросов.
    :param user_id: ID пользователя
    :return: None
    """

    hotel_history = get_history_from_db(user_id)
    if hotel_history:

        bot.send_message(user_id, r'*<<<  ИСТОРИЯ ЗАПРОСОВ  \>\>\>*', parse_mode='MarkdownV2')
        for req_id, date_req, city, check_in, check_out, sort_from_db in hotel_history:

            sort = 'По возрастанию стоимости'
            if sort_from_db == 'PHF':
                sort = 'По убыванию стоимости'
            elif sort_from_db == 'DFL':
                sort = 'Ближе к центру'

            bot.send_message(user_id, f'<b>Дата запроса:</b> {date_req}\n'
                                      f'<b>Город:</b> <i>{city}</i>\n'
                                      f'<b>Даты проживания:</b> <i>с {check_in} по {check_out}</i>\n'
                                      f'<b>Сортировка:</b> <i>{sort}</i>',
                             reply_markup=history_keyboard(req_id), parse_mode='HTML')
        bot.send_message(user_id, r'*<<<  КОНЕЦ ИСТОРИИ ЗАПРОСОВ  \>\>\>*', parse_mode='MarkdownV2')

    else:
        bot.send_message(user_id, 'История запросов пуста.')

    # step(user_id, 1)


@bot.callback_query_handler(func=lambda call: call.data.startswith('set_from_req:'))
def set_from_req(call: CallbackQuery) -> None:
    """
    Установка текущих данных пользователя по данным прошлого запроса при нажатии инлайн кнопки.
    Если дата заезда из запроса меньше текущей, то устанавливается дата заезда: сегодня, выезд: завтра.
    """
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    req = call.data.replace('set_from_req:', '')
    record = get_req_from_db(req)
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

    step(user_id, 2)


@bot.callback_query_handler(func=lambda call: call.data.startswith('hotel_from_req:'))
def hotel_from_req(call: CallbackQuery) -> None:
    """
    Отправка сообщений с отелями запроса из истории.
    :param call:
    :return:
    """
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    req = call.data.replace('hotel_from_req:', '')
    hotels = get_hotel_by_req(req)
    data = get_req_from_db(req)
    print(data)
    bot.send_message(user_id, f'<b><u>!!!  Отели из запроса от {data[0]}  !!!</u></b>\n'
                              f'<b>Город:</b> <i>{data[2]}</i>\n'
                              f'<b>Даты проживания:</b> <i>с {data[3]} по {data[4]}</i>',
                     parse_mode='HTML')
    send_hotels(hotels, user_id)
    bot.send_message(user_id, r'*^^^ ОТЕЛИ ИЗ ПРОШЛОГО ЗАПРОСА  ^^^*', parse_mode='MarkdownV2')
    step(user_id, 1)
