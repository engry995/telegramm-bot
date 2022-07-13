from loader import bot
from telebot.types import User, CallbackQuery
from keyboards.inline import step1_keyboard, step2_keyboard
from utils.utils import get_user_data
from typing import Union


def step(user_id: Union[CallbackQuery, int], st: int = 1) -> None:
    """
    Базовое сообщение, выводится текущий город и даты проживания.
    :param st: номер шага на котором находится пользователь\
                 1 - ввод города, дат, возможность вызова истории
                 2 - вызов информации от отелей с различными сортировками,
                     возможность изменить кол-во отелей и вывод фото.
    :param user_id: ID пользователя или CallbackQuery. Если пользователь, то выводится новое сообщение
                 с соответствующей клавиатурой, если CallbackQuery, то изменятеся клавиатура у текущего сообщения.
    :return: None
    """
    call = None
    if isinstance(user_id, CallbackQuery):
        call = user_id
        user_id = call.from_user.id

    state = get_user_data(user_id)
    print('Из степ:', state)

    keyboard = None
    if st == 1:
        keyboard = step1_keyboard()
    elif st == 2:
        keyboard = step2_keyboard(state['number_hotels'], state['foto'])

    if isinstance(call, CallbackQuery):
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=keyboard)
    else:
        bot.send_message(user_id, f'<b>Текущий город:</b> <i>{state["city"]}</i>\n'
                                  f'<b>Даты проживания:</b> <i>с {state["check_in"].strftime("%d.%m.%Y")} по '
                                  f'{state["check_out"].strftime("%d.%m.%Y")}</i>\n'
                                  f'<b>Количество суток:</b> <i>{(state["check_out"] - state["check_in"]).days}</i>',
                         reply_markup=keyboard, parse_mode='HTML')
