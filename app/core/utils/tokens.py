import os
from dotenv import load_dotenv

from aiogram.types import Message
from sqlalchemy.exc import SQLAlchemyError

from core.bot import BOT_OBJ
from models import Users, Pings
from core.database import Session

load_dotenv()
SMTHNG_WRONG = os.getenv('SMTHNG_WRONG')
LOGS_CHAT_ID = os.getenv('LOGS_CHAT')
session = Session()

async def add_one_ping(ping: str, user: Users, message: Message):
    """Add one ping to user.

    :param ping: Пинг для пользователя
    :type ping: str

    :param user: Пользователь которому добавляется пинг
    :type user: app.core.models.Users

    :param message: Сообщение которое стригерело создание пинга
    :type message: aiogram.types.Message

    :return: None
    :rtype: None
    """
    new_ping = Pings(
        ping_name = ping,
        user_id=user.id,
        count=0,
    )
    try:
        session.add(new_ping)
        await session.commit()
    except SQLAlchemyError as error:
        await message.reply_sticker(sticker=SMTHNG_WRONG)
        await BOT_OBJ.send_message(
            chat_id=LOGS_CHAT_ID,
            text=f'When i has been adding ping - {ping} for user - {user.nickname} to database SQLAlchemyError was rised.\nError: {error}',
            )
        await session.rollback()