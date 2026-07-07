from sqlalchemy import BigInteger, String
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import TYPE_CHECKING
from .base import Base

if TYPE_CHECKING:
    from .category import Category


class User(Base):
    __tablename__ = "users"
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String)
    full_name: Mapped[str | None] = mapped_column(String)
    categories: Mapped[list["Category"]] = relationship(back_populates="user")
