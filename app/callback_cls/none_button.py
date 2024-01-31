"""Callback for empty button in bill."""
from aiogram.filters.callback_data import CallbackData


class NoneButton(CallbackData, prefix='x'):
    name: str