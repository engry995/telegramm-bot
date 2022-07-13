from loader import bot
from telebot.types import Message
import handlers.custom_heandlers.related
from states.user_states import UserState


@bot.message_handler(commands=['start'])
def bot_start(message: Message) -> None:
    """
    Первое сообщение при запуске бота. Установка первоначальных данных пользователя.
    :param message:
    :return:
    """
    bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}!")
    bot.send_message(message.chat.id, f'Вызов справки /help')
    bot.send_message(message.chat.id, 'Здесь можно посмотреть информацию от отелях с сайта Hotels.com')

    bot.delete_state(message.from_user.id, message.chat.id)  # удаляем сохраненные данные
    bot.set_state(message.from_user.id, UserState.all, message.chat.id)

    handlers.custom_heandlers.related.step(message.from_user.id, 1)
