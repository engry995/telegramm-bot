from telebot.handler_backends import State, StatesGroup


class UserState(StatesGroup):
    city = State()  # выбор города
    city_received = State()  # город найден
    check_in = State()  # выбор даты заезда
    check_out = State()  # выбор даты выезда
    all = State()  # все данные получены
