"""Package wich contains of callback query filters classes.

More info about this type of filters `here<https://docs.aiogram.dev/en/latest/dispatcher/filters/callback_data.html>`_

* :menuselector: `callback_cls --> cost_callback.py`

* :menuselector: `callback_cls --> overall_callback.py`
"""
from .cost_callback import CostCallback
from .overall_callback import OverallCallback

__all__ = ['CostCallback', 'OverallCallback']