from loader import bot
import handlers
import database
from utils.utils import listener


if __name__ == '__main__':

    bot.set_update_listener(listener)
    bot.infinity_polling()
