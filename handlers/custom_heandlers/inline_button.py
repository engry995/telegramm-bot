import handlers.custom_heandlers
from loader import bot
from telebot.types import CallbackQuery
from keyboards.inline import step2_keyboard
from config_data.config import NUMBER_OF_FOTO
"""
Обработчики инлайн кнопок
"""


@bot.callback_query_handler(func=lambda call: call.data == 'step1')
def get_date(call: CallbackQuery) -> None:
    """
    Кнопка, возвращающая на экран 1 (выбор города, даты, история)
    """
    bot.answer_callback_query(call.id)
    handlers.custom_heandlers.related.step(call, 1)


@bot.callback_query_handler(func=lambda call: call.data == 'step2')
def get_date(call: CallbackQuery) -> None:
    """
    Кнопка, возвращающая на экран 2 (запрос отелей)
    """
    bot.answer_callback_query(call.id)
    handlers.custom_heandlers.related.step(call, 2)


@bot.callback_query_handler(func=lambda call: call.data.startswith('/'))
def command(call: CallbackQuery):
    """
    Обработчик команд в инлайн-кнопках
    Если callback_data='/command' то выполнится функция связанная с этой командой
    если такой команды нет, сработает assert
    """
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    com = call.data
    if com in ['/lowprice', '/highprice', '/bestdeal']:
        handlers.custom_heandlers.base.handler_command(user_id, com)
    elif com == '/history':
        bot.delete_message(call.from_user.id, call.message.id)
        handlers.custom_heandlers.history.history(user_id)
    else:
        assert False,  f'В инлайн кнопке прописана несуществующая команда {com}'


@bot.callback_query_handler(func=lambda call: call.data == 'need_foto')
def change_show_foto(call: CallbackQuery) -> None:
    """
    Установка режима вывода фото, либо 0, либо NUMBER_OF_FOTO из файла конфигурации
    """
    bot.answer_callback_query(call.id)
    with bot.retrieve_data(call.from_user.id) as data:
        num = data['number_hotels']
        foto = data['foto']
        if foto:
            data['foto'] = 0
        else:
            data['foto'] = NUMBER_OF_FOTO  # количество фото по умолчанию
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=step2_keyboard(num, not foto))


@bot.callback_query_handler(func=lambda call: call.data == 'number_hotels')
def change_number_hotels(call: CallbackQuery) -> None:
    """
    Смена количества выводимых отелей от 5 до 30 с шагом 5.
    """
    bot.answer_callback_query(call.id)
    with bot.retrieve_data(call.from_user.id) as data:
        foto = data['foto']
        num = data['number_hotels']
        if num < 30:
            num += 5
        else:
            num = 5
        data['number_hotels'] = num
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=step2_keyboard(num, foto))
