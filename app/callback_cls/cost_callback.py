from aiogram.filters.callback_data import CallbackData


class CostCallback(CallbackData, prefix='cost'):
    name: str
    cost: int
