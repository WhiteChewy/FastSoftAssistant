import asyncio
import logging
import os
import sys
import string
from dotenv import load_dotenv

from aiogram import Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram import F
from aiogram.types import Message

from middlewares import AlbumMiddleware
from core.texts.start_message import HELLO_MESSAGE

from routers import all_routers
from core.bot import BOT_OBJ

load_dotenv()
# working with bill
BILL_DIR = os.getenv('BILLS_DIR')
PER_PAGE = int(os.getenv('KEYBOARD_CAPACITY'))
# Getting stickers ids
WORKING = os.getenv('WORKING_STCKR')
WRONG_TYPE = os.getenv('WRONG_TYPE_STCKR')
HELLO = os.getenv('HELLO_STICKER')
# Bot object
bot = BOT_OBJ
# Dispatcher is father for handlers
dp = Dispatcher()



@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """Handler wich rescive messages with `/start` command
    
    :param message: Message object
    :type message: aiogram.types.Message
    """
    await message.reply_sticker(HELLO)
    await message.answer(HELLO_MESSAGE)


# @dp.message(F.text.lower().regexp(r'(слыш)ь*(,)* *бай|ув(а|о)жаемы(й|е) *бай'))
# async def parse_bot_command(message: Message) -> None:
#     """Parse human-like commands."""
#     pass


async def main() -> None:
    dp.message.middleware(AlbumMiddleware())
    for router in all_routers:
        dp.include_router(router)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())