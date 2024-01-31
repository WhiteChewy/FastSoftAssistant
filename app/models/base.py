from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


meta = MetaData()


class Base(AsyncAttrs, DeclarativeBase):
    """Модель описывающая базовый класс для SQLAlchemy."""
