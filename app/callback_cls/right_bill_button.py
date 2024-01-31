"""Callback for going to next page on bill."""
from aiogram.filters.callback_data import CallbackData


class RightButton(CallbackData, prefix='>'):
    name: str
    page_number: int
