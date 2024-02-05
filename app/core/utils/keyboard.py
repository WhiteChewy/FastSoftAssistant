from typing import Dict, List

from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from callback_cls import CostCallback


async def create_keyboard_for_bill(lines: Dict[str, int]) -> List:
    """Creating Inline Keyboard Markup for bill.

    :param lines: Dict of position names
    :type lines: Dict[str]

    :return:  Inline keyboard markup with positions from bills
    :rtype: aiogram.types.InlineKeyboardMarkup
    """
    result = []
    for key in lines:
        key_line = InlineKeyboardButton(
            text=key,
            callback_data=CostCallback(name='cost', pos_name=key, cost=lines[key]).pack(),
        )
        result.append([key_line])

    return result