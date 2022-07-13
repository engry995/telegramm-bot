from loader import bot
from telebot.types import CallbackQuery
import handlers.custom_heandlers.related
from keyboards.inline import calendar_keyboard
from states.user_states import UserState
from datetime import datetime, date


@bot.callback_query_handler(func=lambda call: call.data == 'date')
def get_date(call: CallbackQuery) -> None:
    """
    Выбор дат заезда
    """
    bot.answer_callback_query(call.id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
    bot.set_state(call.from_user.id, UserState.check_in, call.message.chat.id)
    bot.send_message(call.message.chat.id, 'Дата заезда >>>',
                     reply_markup=calendar_keyboard(date.today().year, date.today().month))


@bot.callback_query_handler(func=lambda call: call.data.startswith('date:'))
def check_date(call: CallbackQuery) -> None:
    """
    Установка даты заезда или отъезда в зависимости от текущего состояния пользователя.
    """
    date_current = datetime.strptime(call.data, 'date:%Y-%m-%d').date()
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    if bot.get_state(user_id, chat_id) == UserState.check_in.name:
        if date_current < date.today():
            bot.answer_callback_query(call.id, 'Дата меньше текущей', show_alert=True)
        else:
            with bot.retrieve_data(user_id, chat_id) as data:
                data['check_in'] = date_current
            bot.answer_callback_query(call.id, f'Дата заезда: {date_current}\nВыберите дату отъезда.', show_alert=True)
            bot.set_state(user_id, UserState.check_out, chat_id)
            bot.edit_message_text(f'Дата заезда: {date_current}\nДата отъезда >>>', call.message.chat.id, call.message.id,
                                  reply_markup=calendar_keyboard(date_current.year, date_current.month))
    elif bot.get_state(user_id, chat_id) == UserState.check_out.name:
        with bot.retrieve_data(user_id, chat_id) as data:
            date_check_in = data['check_in']
        if date_check_in >= date_current:
            bot.answer_callback_query(call.id, 'Дата выезда раньше заезда!', show_alert=True)
        else:
            with bot.retrieve_data(user_id, chat_id) as data:
                data['check_out'] = date_current
            bot.answer_callback_query(call.id, f'Дата выезда: {date_current}\n'
                                               f'Дней проживания: {(date_current - date_check_in).days}',
                                      show_alert=True)
            bot.set_state(user_id, UserState.all, chat_id)
            bot.edit_message_text('Даты выбраны', call.message.chat.id, call.message.id)
            handlers.custom_heandlers.related.step(user_id, 1)
    else:
        bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('month:'))
def change_month(call: CallbackQuery) -> None:
    """
    Смена месяца при выборе даты.
    """
    bot.answer_callback_query(call.id)
    if bot.get_state(call.from_user.id, call.message.chat.id) in [UserState.check_in.name, UserState.check_out.name]:
        year, month = map(int, call.data.replace('month:', '').split())
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=calendar_keyboard(year, month))


@bot.callback_query_handler(func=lambda call: call.data == 'empty')
def empty(call: CallbackQuery) -> None:
    """
    Обработка пустых клеток при выборе даты.
    """
    bot.answer_callback_query(call.id)

