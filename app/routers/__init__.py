"""All routters for bot.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* :menuselector: routers --> bill_router.py  -- Bahroma bill router
* :menuselector: routers --> social_bot.py   -- Social Status Bot
"""
from .bill_router import BILL_ROUTER
from .social_bot import SOCIAL_BOT_ROUTER
from .ping_bot import PING_BOT


__all__ = ['BILL_ROUTER', 'SOCIAL_BOT_ROUTER', 'PING_BOT']
all_routers = [BILL_ROUTER, SOCIAL_BOT_ROUTER, PING_BOT]
