import asyncio
import logging
import os
import sys
import string
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, CommandObject
from aiogram import F
from aiogram.types import Message, inline_keyboard_markup, inline_keyboard_button, CallbackQuery
from aiogram.utils.markdown import hbold

from texts.start_message import HELLO_MESSAGE
from bill.image_to_text import get_text_from_bill
from callback_cls import CostCallback, OverallCallback
from aiogram.filters.callback_data import CallbackData


load_dotenv()
# Getting token keep it secure
TOKEN = os.getenv('BOT_TOKEN')
# Getting stickers ids
WORKING = os.getenv('WORKING_STCKR')
bot = Bot(TOKEN, parse_mode=ParseMode.MARKDOWN)
# Dispatcher is father for handlers
dp = Dispatcher()

bill = {}
pings = {
    'ефим' : ['Efimkul'],
    'никита' : ['WhiteChewy'],
    'бай' : ['меня'],
    'куликовы': ['Efimkul', 'WhiteChewy'],
    'все': ['Efimkul', 'WhiteChewy', 'marmota_bobak_bot']
}


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """Handler wich rescive messages with `/start` command
    
    :param message: Message object
    :type message: aiogram.types.Message
    """
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


@dp.message(F.photo)
async def check_to_str(message: Message) -> None:
    """Handler wich recive message with photos"""
    send_message_id = await message.answer_sticker(sticker=WORKING, disable_notification=True)
    text_from_bill = get_text_from_bill(number_of_images=2)
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
    bill.pop(user_name, '')
    await bot.send_message(query.message.chat.id, text=f'@{user_name}, вы потратили: {bill[user_name]} Р')


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
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())