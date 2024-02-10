
import os
from datetime import timedelta, datetime
from dotenv import load_dotenv

from aiogram import Router
from aiogram.enums import ContentType
from aiogram import F
from aiogram.types import Message, ContentType
from sqlalchemy import select, update

from core.texts import ADD_TO_BOT, ADD_TIMEOUT, ADD_TO_MYSELF
from models import SocialBot
from core.database import Session

load_dotenv()
pause = os.getenv('MINS_TO_CHILL')
session = Session()
SOCIAL_BOT_ROUTER = Router()

STICKERS_RATING = {
    "AgADAgADf3BGHA": 20,
    "AgADAwADf3BGHA": -20,
}


async def ensure_user_record(user_id: int, chat_id: int, username: str):
    request = select(SocialBot).filter_by(
        user_id=user_id,
        chat_id=chat_id,
    )
    result_query = await session.execute(request)
    record = result_query.scalars().first()
    if not record:
        record = SocialBot(
            user_id=user_id,
            username=username,
            chat_id=chat_id,
            social_rating=0,
        )
        session.add(record)
    await session.commit()
    return record


@SOCIAL_BOT_ROUTER.message(F.text.lower().regexp(r'(слыш)ь*(,)* *бай(,)* покажи рейтинг|ув(а|о)жаемы(й|е) *бай(,)*  покажи рейтинг'))
async def get_chat_rating(message: Message) -> None:
    """Ask bot for social rating top for chat.

    :param message: Message objec of message that has triggered handler
    :type message: aiogram.types.Message

    :return: Nothing
    :rtype: None
    """
    request = select(SocialBot).filter_by(chat_id=message.chat.id).order_by(SocialBot.social_rating.desc())
    result_query = await session.execute(request)
    rating_from_db = result_query.scalars().all()
    entries = [f"{record.username}: {record.social_rating}" for record in rating_from_db]

    await message.reply('\n'.join(entries))


@SOCIAL_BOT_ROUTER.message(F.content_type == ContentType.STICKER)
async def process_sticker(message: Message) -> None:
    """Handle increasing or decreasing social rating with stickers."""
    if not message.reply_to_message:
        return

    sticker_id = message.sticker.file_unique_id

    if sticker_id not in STICKERS_RATING:
        return

    user = message.from_user
    username = user.username or user.full_name
    reply_user = message.reply_to_message.from_user
    reply_username = reply_user.username or reply_user.full_name
    if reply_user.is_bot:
        await message.reply(ADD_TO_BOT)
        return
    if user.id == reply_user.id:
        await message.reply(ADD_TO_MYSELF)
        return
    reply_user_record = await ensure_user_record(
        user_id=reply_user.id,
        chat_id=message.chat.id,
        username=reply_username,
    )
    user_record = await ensure_user_record(
        user_id=user.id,
        chat_id=message.chat.id,
        username=username,
    )
    if user_record.last_update + timedelta(minutes=int(pause)) > datetime.now():
        await message.reply(ADD_TIMEOUT)
        return

    rating_change = STICKERS_RATING[sticker_id]
    new_value = reply_user_record.social_rating + rating_change
    request = (update(SocialBot)
                .where(SocialBot.user_id==reply_user_record.user_id)
                .where(SocialBot.chat_id==message.chat.id)
                .values(social_rating=new_value))
    await session.execute(request)
    await session.commit()
    if rating_change > 0:
        msg_verb = 'увеличен'
    elif rating_change < 0:
        msg_verb = 'уменьшен'
    else:
        msg_verb = 'не изменился'

    msg = f"""Уважаемый {reply_username}, ваш социальный рейтинг {msg_verb}!
Теперь у вас целых {reply_user_record.social_rating} очков социального рейтинга!"""
    await message.reply(msg)
