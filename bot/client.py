from aiogram import Bot, Dispatcher
from bot.config import Config

bot = Bot(token=Config.BOT_TOKEN)
dp = Dispatcher()
