from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import VARCHAR, ARRAY, INTEGER
from sqlalchemy.orm import mapped_column, Mapped, relationship

from .base import Base


if TYPE_CHECKING:
    from .pings import Pings

class Users(Base):
    """Таблица users в БД бота."""

    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    nickname: Mapped[str] = mapped_column(VARCHAR(length=255))
    telegram_id: Mapped[int] = mapped_column(INTEGER, unique=True)
    pings: Mapped[List['Pings']] =  relationship()
