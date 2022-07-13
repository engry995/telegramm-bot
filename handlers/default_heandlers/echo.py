from telebot.types import Message
from handlers.custom_heandlers.related import step
from loader import bot


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
# В ответ отсылается сообщение с просьбой ввести команду.
@bot.message_handler(state=None)
def bot_echo(message: Message) -> None:
    bot.reply_to(message, f'Выберите команду.')
    step(message.from_user.id, 1)
