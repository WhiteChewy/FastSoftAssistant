import os
import string
from datetime import timedelta, datetime
from dotenv import load_dotenv

from aiogram import Router
from aiogram.enums import ContentType
from aiogram import F
from aiogram.types import Message, ContentType
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError

from core.bot import BOT_OBJ
from core.texts import ADD_TO_BOT, ADD_TIMEOUT, ADD_TO_MYSELF
from models import Users, Pings
from core.database import Session

load_dotenv()
SMTHNG_WRONG = os.getenv('SMTHNG_WRONG')
LOGS_CHAT_ID = os.getenv('LOGS_CHAT')
PING_BOT = Router()
session = Session()
bot = BOT_OBJ


@PING_BOT.message(F.text.lower().regexp(r'(слыш)ь*(,)* бай я больше не |ув(а|о)жаемы(й|е) бай(б)* я больше не '))
async def delete_ping(message: Message) -> None:
    """Deleting cast for user.

    :param message: Message object
    :type message: aiogram.types.Message

    :return: None
    :rtype: None
    """
    message_without_punctuation = message.text.translate(str.maketrans('', '', string.punctuation))
    ping = message_without_punctuation.split()[5]
    request = select(Pings).join(Users, Pings.user_id==Users.id).where(
        Pings.ping_name==ping,
        Users.telegram_id==message.from_user.id,
    )
    try:
        query = await session.execute(request)
        pings = query.scalars().all()
        for ping in pings:
            await session.delete(ping)
            await session.commit()
    except SQLAlchemyError as error:
        await message.reply_sticker(sticker=SMTHNG_WRONG)
        await BOT_OBJ.send_message(
            chat_id=LOGS_CHAT_ID,
            text=f'Tried to find all pings. But error occured.\nError: {error}',
            )
        await session.rollback()
        return
    
    await message.reply(text=f'Готово, вы больше не {ping.ping_name}')


@PING_BOT.message(F.text.lower().regexp(r'(слыш)ь*(,)* бай(,)* я |ув(а|о)жаемы(й|е) бай(,)* я '))
async def add_ping(message: Message) -> None:
    """Add ping cast to user.
    
    :param message: Message that triggers F.filter
    :type message: aiogram.types.Message

    :return: None
    :rtype: None
    """
    message_without_punctuation = message.text.translate(str.maketrans('', '', string.punctuation))
    words_without_command = message_without_punctuation.split()[3:]
    ping = words_without_command[0]
    username = message.from_user.username if message.from_user.username else message.from_user.full_name
    user_telegram_id = message.from_user.id

    request = select(Users).filter_by(
        telegram_id=message.from_user.id
    )
    try:
        result_query = await session.execute(request)
    except SQLAlchemyError as error:
        await message.reply_sticker(sticker=SMTHNG_WRONG)
        await BOT_OBJ.send_message(
            chat_id=LOGS_CHAT_ID,
            text=f'SQLAlchemyError was rised when i tried to find {username} in DB.\nError: {error}',
            )
        return
    user = result_query.scalars().first()
    # Если пользователь новый
    if not user:
        try:
            record = Users(
                nickname=username,
                telegram_id=user_telegram_id,
            )
            session.add(record)
        except SQLAlchemyError as error:
            await message.reply_sticker(sticker=SMTHNG_WRONG)
            await BOT_OBJ.send_message(
                chat_id=LOGS_CHAT_ID,
                text=f'When i has been adding user {username} to database SQLAlchemyError was rised.\nError: {error}',
                )
            await session.rollback()
            return
        await session.commit()
        user = await session.execute(select(Users).filter_by(telegram_id=user_telegram_id))
        user = user.scalars().first()
    request = select(Pings).filter_by(
        ping_name=ping,
        user_id=user.id,
    )
    try:
        result_query = await session.execute(request)
    except SQLAlchemyError as error:
        await message.reply_sticker(sticker=SMTHNG_WRONG)
        await BOT_OBJ.send_message(
            chat_id=LOGS_CHAT_ID,
            text=f'SQLAlchemyError was rised when i tried to find ping: {ping} for {username} in DB.\nError: {error}',
            )
        return
    ping_find_req = select(Pings).filter_by(
        user_id=user.id,
        ping_name=ping,
    )
    # Check if user already has this ping
    try:
        ping_result = await session.execute(ping_find_req)
        ping_result = ping_result.scalars().first()
    except SQLAlchemyError as error:
        await message.reply_sticker(sticker=SMTHNG_WRONG)
        await BOT_OBJ.send_message(
            chat_id=LOGS_CHAT_ID,
            text=f'When i has been adding user {username} to database SQLAlchemyError was rised.\nError: {error}',
            )
        await session.rollback()
        return
    if ping_result:
        await message.reply(
            text=f'''Уважаемый, я уже знаю вас как {ping}. Для просмотра всех доступных кастов для вас введите
```
Слышь, Бай, кто я?
```
или
```
/ping_show @никнейм
```
'''
        )
        return
    new_ping = Pings(
        ping_name = ping,
        user_id=user.id,
        count=0,
    )
    # Add ping to database
    try:
        session.add(new_ping)
        await session.commit()
    except SQLAlchemyError as error:
        await message.reply_sticker(sticker=SMTHNG_WRONG)
        await BOT_OBJ.send_message(
            chat_id=LOGS_CHAT_ID,
            text=f'When i has been adding ping - {ping} for user - {username} to database SQLAlchemyError was rised.\nError: {error}',
            )
        await session.rollback()
        return
    await message.reply(
        text=f'Приятно похнакомится, {ping}'
    )


@PING_BOT.message(F.text.lower().regexp(r'(слыш)ь*(,)* бай(,)* кто (@)*|ув(а|о)жаемы(й|е) бай(,)* кто (@)*'))
async def show_ping(message: Message) -> None:
    """Show all pings for user.

    :param message: Message Object
    :type message: aiogram.types.Message

    :return: None
    :rtype: None
    """
    message_without_punctuation = message.text.translate(str.maketrans('', '', string.punctuation))
    words_without_command = message_without_punctuation.split()[3:]
    who = words_without_command[0]

    if who == 'я':
        username = message.from_user.username if message.from_user.username else message.from_user.full_name
    else:
        username = who
    
    request = select(Pings).join(Users, Pings.user_id == Users.id).filter_by(
        nickname=username
    )
    try:
        query = await session.execute(request)
        rows = query.scalars().all()
    except SQLAlchemyError as error:
        await message.reply_sticker(sticker=SMTHNG_WRONG)
        await BOT_OBJ.send_message(
            chat_id=LOGS_CHAT_ID,
            text=f'Tried to find all pings for username: {username}. But error occured.\nError: {error}',
            )
        await session.rollback()
        return
    
    msg_about = ', '.join([f'{p.ping_name}: {p.count} раз' for p in rows])
    await message.answer(text=f'Уважаемый {username} известен как:\n'+msg_about)


@PING_BOT.message(F.text.lower().regexp(r'(слыш)ь*(,)* |ув(а|о)жаемы(й|е) '))
async def ping_someone(message: Message) -> None:
    """Cast someone by ping_name.

    :param message: Message that triggers cast
    :type message: aiogram.types.Message

    :return: None
    :rtype: None
    """
    message_without_punctuation = message.text.translate(str.maketrans('', '', string.punctuation))
    words_without_command = message_without_punctuation.split()[1:]
    words = set(words_without_command)
    all_pings = select(Pings)
    try:
        query = await session.execute(all_pings)
        all_pings = query.scalars().all()
    except SQLAlchemyError as error:
        await message.reply_sticker(sticker=SMTHNG_WRONG)
        await BOT_OBJ.send_message(
            chat_id=LOGS_CHAT_ID,
            text=f'Tried to find all pings. But error occured.\nError: {error}',
            )
        await session.rollback()
        return
    pings_set = {elem.ping_name for elem in all_pings}
    result_pings = pings_set & words
    nicknames = set()
    # Get nicknames of casted people
    for ping in result_pings:
        request = select(Pings).filter_by(
            ping_name=ping
        )
        query = await session.execute(request)
        pings_list = query.scalars().all()
        user_ids = {ping.user_id for ping in pings_list}
        request = select(Users).where(Users.id.in_(user_ids))
        query = await session.execute(request)
        users = query.scalars().all()
        nicknames = nicknames | {user.nickname for user in users}
    # Make message for cast if nicknames
    if not nicknames:
        return
    msg = '@' + ' @'.join(nicknames)
    # Edit counters for number of pings
    for ping in pings_set:
        request = select(Pings).filter_by(ping_name=ping)
        pings = await session.execute(request)
        pings = pings.scalars().all()
        for p in pings:
            request = update(Pings).where(Pings.id==p.id).values(
                count=p.count+1
            )
            await session.execute(request)
            await session.commit()
    await message.reply(text=msg)
