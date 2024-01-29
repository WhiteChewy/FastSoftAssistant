import asyncio
import logging
import os
import sys
import string
from dotenv import load_dotenv
from typing import List

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode, ContentType
from aiogram.filters import CommandStart, Command
from aiogram import F
from aiogram.types import (InputMediaPhoto, InputMedia, Message, inline_keyboard_markup,
                            inline_keyboard_button, CallbackQuery, ContentType as CT)
from aiogram.utils.markdown import hbold
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from aiogram.filters.callback_data import CallbackData

from middlewares import AlbumMiddleware
from texts.start_message import HELLO_MESSAGE
from bill.image_to_text import get_text_from_bill
from callback_cls import CostCallback, OverallCallback
from models import Users, Pings

load_dotenv()
BILL_DIR = os.getenv('BILLS_DIR')
# Getting token keep it secure
TOKEN = os.getenv('BOT_TOKEN')
# Getting stickers ids
WORKING = os.getenv('WORKING_STCKR')
WRONG_TYPE = os.getenv('WRONG_TYPE_STCKR')
HELLO = os.getenv('HELLO_STICKER')
bot = Bot(TOKEN, parse_mode=ParseMode.MARKDOWN)
# Dispatcher is father for handlers
dp = Dispatcher()
engine = create_async_engine('sqlite+aiosqlite:///bot_db.db', echo=True)
Session = async_sessionmaker(engine, expire_on_commit=False)
bill = {}


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """Handler wich rescive messages with `/start` command
    
    :param message: Message object
    :type message: aiogram.types.Message
    """
    await message.reply_sticker(HELLO)
    await message.answer(HELLO_MESSAGE)


@dp.message(F.text.lower().regexp(r'(слыш)ь*(,)* |ув(а|о)жаемы(й|е)(,)* '))
async def parse_cast_message(message: Message) -> None:
    """Ping persons in chat.

    Ping user in chat due to saved ping name. Name saved in database. And added by another command.

    :param message: Message that trigger filter
    :type message: aiogram.types.Message

    :return: Nothong
    :rtype: None
    """
    message_without_punctuations = message.text.lower().translate(str.maketrans('', '', string.punctuation))
    data_to_parse = message_without_punctuations.split()
    msg = ''
    
    await message.reply(text=f'Слышу, слышу. Ты обратился к {msg}')


@dp.message(F.text.lower().regexp(r'(слыш)ь*(,)* *бай|ув(а|о)жаемы(й|е)(,)* *бай'))
async def parse_bot_command(message: Message) -> None:
    """Parse human-like commands."""
    pass


@dp.message(F.content_type.in_([CT.PHOTO, CT.VIDEO, CT.AUDIO, CT.DOCUMENT]))
async def check_to_str(message: Message, album: List[Message]) -> None:
    """Handler wich recive message with photos"""
    if message.content_type != ContentType.PHOTO:
        await message.reply_sticker(WRONG_TYPE, disable_notification=True)
        await message.answer(text=f'Уважаемый @{message.from_user.username}, вы должны были отправить фотографии чека с Бахромы... Но я что то их не наблюдаю.')
    else:
        send_message_id = await message.reply_sticker(sticker=WORKING, disable_notification=True)
        # Getting file_ids from media group 
        media_group = []
        for msg in album:
            if msg.photo:
                file_id = msg.photo[-1].file_id
                media_group.append(file_id)
        for index, elem in enumerate(media_group):
            await bot.download(elem, f'{BILL_DIR}/{index}.jpg')
        text_from_bill = get_text_from_bill(number_of_images=len(media_group))
        await send_message_id.delete()
        msg_text = 'Вот ваш счет'
        keyboard_buttons = []
        for key in text_from_bill:
            key_line = inline_keyboard_button.InlineKeyboardButton(
                text=key,
                callback_data=CostCallback(name='cost', cost=text_from_bill[key]).pack(),
            )
            keyboard_buttons.append([key_line])
        overall = inline_keyboard_button.InlineKeyboardButton(
            text='Посчитай пожалуйста',
            callback_data=OverallCallback(text='overall').pack(),
        )
        keyboard_buttons.append([overall])
        keyboard = inline_keyboard_markup.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

        await message.answer(text=msg_text, reply_markup=keyboard)


@dp.callback_query(OverallCallback.filter(F.text == 'overall'))
async def print_overall(query: CallbackQuery, callback_data: CallbackData, bot: Bot):
    await query.answer()
    user_name = query.from_user.username
    await bot.send_message(query.message.chat.id, text=f'@{user_name}, вы потратили: {bill[user_name]} Р')
    bill.pop(user_name, '')


@dp.callback_query(CostCallback.filter(F.name == 'cost'))
async def calculate_callbacks(query: CallbackQuery, callback_data: CostCallback):
    """Calculates how much the user has to pay, depending on the buttons he pressed.

    :param query:
    :type query:

    :param callback_data:
    :type callback_data:

    :return:
    :rtype: 
    """
    await query.answer()
    cost = callback_data.cost
    user_name = query.from_user.username
    if user_name in bill:
        bill[user_name] += cost
    else:
        bill[user_name] = cost
    logging.info('%s нажал на товар со стоймостью: %s', user_name, cost)

async def main() -> None:
    dp.message.middleware(AlbumMiddleware())
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())