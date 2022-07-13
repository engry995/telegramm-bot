from loader import bot
from telebot.types import CallbackQuery, Message
from keyboards.reply import city_choice, request_location
from states.user_states import UserState
import handlers.custom_heandlers.related
from utils.api_hotels import get_destination, reverse_geocode


@bot.message_handler(commands=['city'])  # команда выбора города
def city_com(message: Message) -> None:
    bot.set_state(message.from_user.id, UserState.city, message.chat.id)
    bot.send_message(message.chat.id, 'Введите город для поиска >>>', reply_markup=request_location())


@bot.callback_query_handler(func=lambda call: call.data == 'city')  # выбор города через инлайн кнопку
def city_inl(call: CallbackQuery):
    bot.answer_callback_query(call.id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
    bot.set_state(call.from_user.id, UserState.city, call.message.chat.id)
    bot.send_message(call.message.chat.id, 'Введите город для поиска >>>', reply_markup=request_location())


@bot.message_handler(content_types=['location'])  # получение текущего города пользователя через геолокацию
def get_location(message: Message) -> None:
    city = reverse_geocode(message.location.latitude, message.location.longitude)
    print('получена геолокация:', city)
    city_option(message, city)


@bot.message_handler(state=UserState.city)
def city_rep(message: Message) -> None:
    city_option(message, message.text)


def city_option(message: Message, city: str) -> None:
    """
    Отправка пользователю локаций, подходящих под его запрос, для уточнения.
    :param message: сообщение пользователя.
    :param city: название города, введенного пользователем для поиска.
    :return: None
    """
    user_id = message.from_user.id
    chat_id = message.chat.id

    cities = get_destination(city)

    if cities is None:
        bot.send_message(chat_id, 'Данные не получены. Повторите попытку позже.')
    elif cities:
        bot.set_state(user_id, UserState.city_received, chat_id)
        with bot.retrieve_data(user_id, chat_id) as data:
            data['city'] = cities
        bot.send_message(chat_id, 'Уточните поиск >>>', reply_markup=city_choice(cities))
    else:
        bot.send_message(chat_id, f'По запросу "{city}" ничего не найдено.\n'
                                  f'Попробуйте еще раз.\n'
                                  f'Введите город для поиска >>>')


@bot.message_handler(state=UserState.city_received)
def city_received(message: Message) -> None:
    """
    Функция вызывается при получении от пользователя уточненной локации.
    Если текст соответствует предложенным локациям, то обновляются данные и состояние пользователя.
    :param message: сообщение пользователя
    :return:
    """
    user_id = message.from_user.id
    with bot.retrieve_data(user_id, message.chat.id) as data:
        cities = data['city']

    if message.text in cities:
        # Если текст соответствует словарю, то в city сохраняем город, в city_id его id
        with bot.retrieve_data(user_id, message.chat.id) as data:
            data['city_id'] = cities[message.text]
            data['city'] = message.text

        bot.set_state(user_id, UserState.all, message.chat.id)
        handlers.custom_heandlers.related.step(user_id, 1)
    else:
        bot.send_message(message.chat.id, 'Уточните поиск >>>', reply_markup=city_choice(cities))
