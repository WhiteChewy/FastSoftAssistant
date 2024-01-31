from datetime import datetime

from sqlalchemy import INTEGER, BIGINT, VARCHAR, DATETIME
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class SocialBot(Base):

    __tablename__ = "social_bot"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    user_id: Mapped[int] = mapped_column(BIGINT)
    username: Mapped[str] = mapped_column(VARCHAR(255))
    social_rating: Mapped[int] = mapped_column(INTEGER)
    chat_id: Mapped[int] = mapped_column(BIGINT)
    last_update: Mapped[datetime] = mapped_column(DATETIME, default=datetime.min)
