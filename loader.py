from telebot import TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from config_data import config
from utils.set_bot_commands import set_default_commands

storage = StateMemoryStorage()
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)
set_default_commands(bot)
bot.add_custom_filter(custom_filters.StateFilter(bot))
