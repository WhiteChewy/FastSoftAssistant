from aiogram.filters.callback_data import CallbackData


class CostCallback(CallbackData, prefix='cost'):
    name: str
    pos_name: str
    cost: int
