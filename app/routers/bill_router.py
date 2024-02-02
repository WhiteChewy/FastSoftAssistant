import logging
import os
import re
from dotenv import load_dotenv
from typing import List

from aiogram import Bot, Router
from aiogram.enums import ParseMode
from aiogram import F
from aiogram.types import (Message, inline_keyboard_markup, inline_keyboard_button,
CallbackQuery, ContentType as CT)
from aiogram.filters.callback_data import CallbackData

from core.filter.check_message import CheckMessage
from core.bill_utils.image_to_text import get_text_from_bill
from callback_cls import CostCallback, OverallCallback, NoneButton, LeftButton, RightButton
from core.utils.keyboard import create_keyboard_for_bill
from core.bot import BOT_OBJ

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
LOGS_CHAT = os.getenv('LOGS_CHAT')
# Routers is father for handlers
BILL_ROUTER = Router()
bot = BOT_OBJ
# globals
bill = {}
all_inline_keys = []


# Здесь можно было бы спрятать проверку на re.compile в кастомный класс фильтр, НО тогда неверно отрабатывает middleware
@BILL_ROUTER.message(F.content_type.in_([CT.PHOTO]))
async def check_to_str(message: Message, album: List[Message]) -> None:
    """Handler wich recive message with media group."""
    global all_inline_keys
    ping_re = re.compile(r'(слыш)ь*(,)* *бай(,)* посчитай(те)*|ув(а|о)жаемы(й|е)(,)* *бай *(по|рас)считай(те)*')
    if ping_re:
        send_message_id = await message.reply_sticker(sticker=WORKING, disable_notification=True)
        # Getting file_ids from media group 
        media_group = []
        if message.media_group_id:
            for msg in album:
                if msg.photo:
                    file_id = msg.photo[-1].file_id
                    media_group.append(file_id)
        else:
            file_id = message.photo[-1].file_id
            media_group.append(file_id)
        for index, elem in enumerate(media_group):
            await bot.download(elem, f'{BILL_DIR}/{index}.jpg')
        try:
            text_from_bill = get_text_from_bill(number_of_images=len(media_group))
            await send_message_id.delete()
        except Exception as error:
            await bot.send_message(chat_id=int(LOGS_CHAT), text=f'DURING EXTRACTION TEXT FROM IMAGE ERROR OCCURED.\n\nError {error}')
        msg_text = '''Вот ваш счет.
        Пожалуйста выберете что вы хотите посчитать'''
        all_inline_keys = await create_keyboard_for_bill(text_from_bill)
        total_pages = (len(all_inline_keys) // PER_PAGE) + 1
        # prev = inline_keyboard_button.InlineKeyboardButton(
        #     text='X',
        #     callback_data=NoneButton(name="why_it_cant_be_none_jesus").pack(),
        # )
        # mid = inline_keyboard_button.InlineKeyboardButton(
        #     text=f'1 из {total_pages}',
        #     callback_data=NoneButton(name="ffs_why_i_must_do_this").pack(),
        # )
        # next = inline_keyboard_button.InlineKeyboardButton(
        #     text = '>',
        #     callback_data=RightButton(name='right', page_number=1).pack(),
        # )
        pay = inline_keyboard_button.InlineKeyboardButton(
            text='Посчитать без скидки',
            callback_data=OverallCallback(text='overall').pack(),
        )
        pay_discount = inline_keyboard_button.InlineKeyboardButton(
            text='Посчитать со скидкой',
            callback_data=OverallCallback(text='overall_discount').pack(),
        )
        list_of_buttons = all_inline_keys[:PER_PAGE]+[[pay, pay_discount]]
        keyboard = inline_keyboard_markup.InlineKeyboardMarkup(
            inline_keyboard=list_of_buttons
        )
        await message.answer(text=msg_text, reply_markup=keyboard)


@BILL_ROUTER.callback_query(RightButton.filter(F.name == 'right'))
async def next_page(query: CallbackQuery, callback_data: RightButton):
    """Create keyboard for bill if right button was pressed."""
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
    if total_pages > multiplier-1:
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
    all_buttons = all_inline_keys[PER_PAGE*multiplier:PER_PAGE*multiplier+PER_PAGE]+[[prev, mid, next]]+[[pay, pay_discount]]
    keyboard = inline_keyboard_markup.InlineKeyboardMarkup(
        inline_keyboard=all_buttons
        )
    await query.message.edit_reply_markup(reply_markup=keyboard)


@BILL_ROUTER.callback_query(LeftButton.filter(F.name == "left"))
async def next_page(query: CallbackQuery, callback_data: RightButton):
    """Create keyboard if left button was pressed."""
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
    all_buttons = all_inline_keys[PER_PAGE*multiplier:PER_PAGE*multiplier+PER_PAGE]+[[prev, mid, next]]+[[pay, pay_discount]]
    keyboard = inline_keyboard_markup.InlineKeyboardMarkup(
        inline_keyboard=all_buttons,
        )
    await query.message.edit_reply_markup(reply_markup=keyboard)



@BILL_ROUTER.callback_query(NoneButton.filter())
async def none_presse(query: CallbackQuery, callback_data: RightButton) -> None:
    """do nothing if none button  was pressed."""
    await query.answer()


@BILL_ROUTER.callback_query(OverallCallback.filter(F.text.in_(['overall', 'overall_discount'])))
async def print_overall(query: CallbackQuery, callback_data: CallbackData):
    await query.answer()
    user_name = query.from_user.username
    price = bill[user_name] if callback_data.text == 'overall' else bill[user_name]/2
    await bot.send_message(query.message.chat.id, text=f'@{user_name}, вы потратили: {price} Р')
    bill.pop(user_name, '')


@BILL_ROUTER.callback_query(CostCallback.filter(F.name == 'cost'))
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
