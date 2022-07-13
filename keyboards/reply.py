from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def city_choice(cities: dict) -> ReplyKeyboardMarkup:
    """
    Клавиатура вариантов подходящих локаций.
    :param cities: словарь {Наименование_локации: ID локации}.
    :return: клавиатура
    """
    keyboard = ReplyKeyboardMarkup(True, one_time_keyboard=True, row_width=1)
    keyboard.add(*[KeyboardButton(city) for city in cities])
    return keyboard


def request_location() -> ReplyKeyboardMarkup:
    """
    Кнопка для определения текущего города по геолокации.
    :return: Клавиатура с одной кнопкой.
    """
    keyboard = ReplyKeyboardMarkup(True, True)
    keyboard.add(KeyboardButton('Отправить свое положение', request_location=True))
    return keyboard
