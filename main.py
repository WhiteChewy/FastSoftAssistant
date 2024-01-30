import asyncio
import logging
import os
import re
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
from callback_cls import CostCallback, OverallCallback, NoneButton, LeftButton, RightButton
from models import Users, Pings
from utils.keyboard import create_keyboard_for_bill

load_dotenv()
# working with bill
BILL_DIR = os.getenv('BILLS_DIR')
PER_PAGE = int(os.getenv('KEYBOARD_CAPACITY'))
# Getting token keep it secure
TOKEN = os.getenv('BOT_TOKEN')
# Getting stickers ids
WORKING = os.getenv('WORKING_STCKR')
WRONG_TYPE = os.getenv('WRONG_TYPE_STCKR')
HELLO = os.getenv('HELLO_STICKER')
# Bot object
bot = Bot(TOKEN, parse_mode=ParseMode.MARKDOWN)
# Dispatcher is father for handlers
dp = Dispatcher()
# Database (aio SQLite3)
engine = create_async_engine('sqlite+aiosqlite:///bot_db.db', echo=True)
Session = async_sessionmaker(engine, expire_on_commit=False)
# globals
bill = {}
all_inline_keys = []


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
    global all_inline_keys
    ping_re = re.compile(r'(слыш)ь*(,)* *бай(,)* посчитай(те)*|ув(а|о)жаемы(й|е)(,)* *бай посчитай(те)*|/bill')
    if message.caption and re.search(ping_re, message.caption.lower()):
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
        msg_text = '''Вот ваш счет.
        Пожалуйста выберете что вы хотите посчитать'''
        all_inline_keys = await create_keyboard_for_bill(text_from_bill)
        total_pages = (len(all_inline_keys) // PER_PAGE) + 1
        prev = inline_keyboard_button.InlineKeyboardButton(
            text='X',
            callback_data=NoneButton(name="why_it_cant_be_none_jesus").pack(),
        )
        mid = inline_keyboard_button.InlineKeyboardButton(
            text=f'1 из {total_pages}',
            callback_data=NoneButton(name="ffs_why_i_must_do_this").pack(),
        )
        next = inline_keyboard_button.InlineKeyboardButton(
            text = '>',
            callback_data=RightButton(name='right', page_number=1).pack(),
        )
        pay = inline_keyboard_button.InlineKeyboardButton(
            text='Посчитать без скидки',
            callback_data=OverallCallback(text='overall').pack(),
        )
        pay_discount = inline_keyboard_button.InlineKeyboardButton(
            text='Посчитать со скидкой',
            callback_data=OverallCallback(text='overall_discount').pack(),
        )
        keyboard = inline_keyboard_markup.InlineKeyboardMarkup(
            inline_keyboard=(all_inline_keys[:PER_PAGE]+[[prev, mid, next]]+[[pay, pay_discount]])
        )
        await message.answer(text=msg_text, reply_markup=keyboard)


@dp.callback_query(RightButton.filter(F.name == 'right'))
async def next_page(query: CallbackQuery, callback_data: RightButton):
    await query.answer()
    global all_inline_keys
    total_pages = (len(all_inline_keys) // PER_PAGE) + 1
    multiplier = callback_data.page_number
    prev = inline_keyboard_button.InlineKeyboardButton(
        text='<',
        callback_data=LeftButton(name="left", page_number=multiplier-1).pack(),
    )
    mid = inline_keyboard_button.InlineKeyboardButton(
        text=f'{callback_data.page_number+1} из {total_pages}',
        callback_data=NoneButton(name="i_hate_that_it_cant_be_none").pack(),
    )
    if total_pages < multiplier-1:
        next = inline_keyboard_button.InlineKeyboardButton(
            text = '>',
            callback_data=RightButton(name='right', page_number=multiplier+1).pack(),
        )
    else:
        next = inline_keyboard_button.InlineKeyboardButton(
            text = 'X',
            callback_data=NoneButton(name='AGAIN_ARGHHHHHH').pack(),
        )
    pay = inline_keyboard_button.InlineKeyboardButton(
        text='Посчитать без скидки',
        callback_data=OverallCallback(text='overall').pack(),
    )
    pay_discount = inline_keyboard_button.InlineKeyboardButton(
        text='Посчитать со скидкой',
        callback_data=OverallCallback(text='overall_discount').pack(),
    )
    keyboard = inline_keyboard_markup.InlineKeyboardMarkup(
        inline_keyboard=(all_inline_keys[PER_PAGE*multiplier:PER_PAGE*multiplier+PER_PAGE]+[[prev, mid, next]]+[[pay, pay_discount]])
        )
    await query.message.edit_reply_markup(reply_markup=keyboard)


@dp.callback_query(LeftButton.filter(F.name == "left"))
async def next_page(query: CallbackQuery, callback_data: RightButton):
    await query.answer()
    global all_inline_keys
    total_pages = (len(all_inline_keys) // PER_PAGE) + 1
    multiplier = callback_data.page_number
    if multiplier != 0:
        prev = inline_keyboard_button.InlineKeyboardButton(
            text='<',
            callback_data=LeftButton(name="left", page_number=multiplier-1).pack(),
        )
    else:
        prev = inline_keyboard_button.InlineKeyboardButton(
            text = 'X',
            callback_data=NoneButton(name='JESUS_CRIST_ITS_NONE').pack(),
        )
    mid = inline_keyboard_button.InlineKeyboardButton(
        text=f'{callback_data.page_number+1} из {total_pages}',
        callback_data=NoneButton(name="i_hate_that_it_cant_be_none").pack(),
    )
    next = inline_keyboard_button.InlineKeyboardButton(
        text = '>',
        callback_data=RightButton(name='right', page_number=multiplier+1).pack(),
    )
    pay = inline_keyboard_button.InlineKeyboardButton(
        text='Посчитать без скидки',
        callback_data=OverallCallback(text='overall').pack(),
    )
    pay_discount = inline_keyboard_button.InlineKeyboardButton(
        text='Посчитать со скидкой',
        callback_data=OverallCallback(text='overall_discount').pack(),
    )
    keyboard = inline_keyboard_markup.InlineKeyboardMarkup(
        inline_keyboard=(all_inline_keys[PER_PAGE*multiplier:PER_PAGE*multiplier+PER_PAGE]+[[prev, mid, next]]+[[pay, pay_discount]])
        )
    await query.message.edit_reply_markup(reply_markup=keyboard)


@dp.callback_query(OverallCallback.filter(F.text == 'overall_discount'))
@dp.callback_query(OverallCallback.filter(F.text == 'overall'))
async def print_overall(query: CallbackQuery, callback_data: CallbackData, bot: Bot):
    await query.answer()
    user_name = query.from_user.username
    price = bill[user_name] if callback_data.text == 'overall' else bill[user_name]/2
    await bot.send_message(query.message.chat.id, text=f'@{user_name}, вы потратили: {price} Р')
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