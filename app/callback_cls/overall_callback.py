from aiogram.filters.callback_data import CallbackData


class OverallCallback(CallbackData, prefix='over'):
    text: str
