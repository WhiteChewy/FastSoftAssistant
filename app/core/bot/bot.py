import dotenv
import os

from aiogram import Bot
from aiogram.enums import ParseMode

dotenv.load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

BOT_OBJ = Bot(TOKEN, parse_mode='HTML')
