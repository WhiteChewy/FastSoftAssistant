from typing import TYPE_CHECKING

from sqlalchemy import INTEGER, VARCHAR, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from .base import Base


if TYPE_CHECKING:
    from .users import Users


class Pings(Base):
    """Таблица Pings содержащая все возможные пинги."""

    __tablename__ = 'pings'
    
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    ping_name: Mapped[str] = mapped_column(VARCHAR(length=255))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    count: Mapped[int] = mapped_column(INTEGER)
    user: Mapped['Users'] = relationship(back_populates='pings')
