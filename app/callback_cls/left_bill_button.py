"""Callback for going to previous page on bill."""
from aiogram.filters.callback_data import CallbackData


class LeftButton(CallbackData, prefix='<'):
    name: str
    page_number: int