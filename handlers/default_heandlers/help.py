from telebot.types import Message
from config_data.config import COMMANDS
from loader import bot


@bot.message_handler(commands=['help'])
def bot_help(message: Message) -> None:
    """
    Отправка списка доступных команд.
    """
    text = [f'/{command} - {desk}' for command, desk in COMMANDS]
    bot.send_message(message.chat.id, '\n'.join(text))
