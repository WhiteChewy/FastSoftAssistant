"""All routters for bot.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* :menuselector: routers --> bill_router.py  -- Bahroma bill router
* :menuselector: routers --> social_bot.py   -- Social Status Bot
"""
from .bill_router import BILL_ROUTER
from .social_bot import SOCIAL_BOT_ROUTER


__all__ = ['BILL_ROUTER', 'SOCIAL_BOT_ROUTER']
all_routers = [BILL_ROUTER, SOCIAL_BOT_ROUTER]
