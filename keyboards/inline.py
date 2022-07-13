from typing import Final
"""
Здесь собраны инлайн клавиатруры.
"""

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import calendar
from datetime import date, timedelta


def step1_keyboard() -> InlineKeyboardMarkup:
    """
    :return: Клавиатура первого шага
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton('Выбрать город', callback_data='city')
    button2 = InlineKeyboardButton('Указать даты', callback_data='date')
    button3 = InlineKeyboardButton('История', callback_data='/history')
    button4 = InlineKeyboardButton('Далее', callback_data='step2')

    keyboard.add(button1, button2, button3, button4)
    return keyboard


def step2_keyboard(number_hotel: int, foto: bool) -> InlineKeyboardMarkup:
    """
    Инлайн клавиатура для второго шага.
    :param number_hotel: количество отелей для вывода
    :param foto: нужно ли выводить фото
    :return: клавиатуру
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton('Недорогие', callback_data='/lowprice')
    button2 = InlineKeyboardButton('Дорогие', callback_data='/highprice')
    button3 = InlineKeyboardButton('Ближе к центру', callback_data='/bestdeal')
    button4 = InlineKeyboardButton('Назад', callback_data='step1')
    button5 = InlineKeyboardButton(f'Кол-во отелей: {number_hotel}', callback_data='number_hotels')
    button6 = InlineKeyboardButton(f'Фото: {"Да" if foto else "Нет"}', callback_data='need_foto')

    keyboard.add(button1, button2, button3, button4, button5, button6)
    return keyboard


def calendar_keyboard(year: int, month: int) -> InlineKeyboardMarkup:
    """
    Инлайн клавиатура-календарь
    :param year: год календаря
    :param month: месяц календаря
    :return: клавиатуру с требуемыми параметрами.
    """
    EMTPY_FIELD: Final[str] = 'empty'
    format_date = '%Y-%m-%d'

    keyboard = InlineKeyboardMarkup(row_width=7)
    keyboard.add(InlineKeyboardButton(text=date(year=year, month=month, day=1).strftime('%b %Y'),
                                      callback_data=EMTPY_FIELD))
    keyboard.add(*[InlineKeyboardButton(text=day, callback_data=EMTPY_FIELD)
                   for day in ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']])

    for week in calendar.Calendar().monthdayscalendar(year=year, month=month):
        week_buttons = []
        for day in week:
            if day != 0:
                day_name = str(day)
                week_buttons.append(InlineKeyboardButton(
                    text=day_name, callback_data='date:' + date(year, month, day).strftime(format_date)))
            else:
                day_name = ' '
                week_buttons.append(InlineKeyboardButton(text=day_name, callback_data=EMTPY_FIELD))
        keyboard.add(*week_buttons)

    # кнопки смены месяца
    form = '%Y %m'
    # чтобы гарантированно попасть в прошлый и будущий месяц, к 15 числу прибавим/отнимем 30 дней
    cur = date(year, month, 15)
    prev_month = (cur - timedelta(30)).strftime(form)
    next_month = (cur + timedelta(30)).strftime(form)
    keyboard.add(InlineKeyboardButton(text='Предыдущий месяц', callback_data=f'month: {prev_month}'),
                 InlineKeyboardButton(text='Следующий месяц', callback_data=f'month: {next_month}'))

    return keyboard


def history_keyboard(req) -> InlineKeyboardMarkup:
    """
    Инлайн клавиатура результатов истории поиска.
    :param req: Номер запроса в базе данных для записи параметра в кнопки.
    :return: Клавиатура
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton('Установить для поиска', callback_data=f'set_from_req:{req}')
    button2 = InlineKeyboardButton('Показать отели', callback_data=f'hotel_from_req:{req}')
    keyboard.add(button1, button2)
    return keyboard
