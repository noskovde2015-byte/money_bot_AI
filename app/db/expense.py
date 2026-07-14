from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, Text, String, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User
    from .category import Category


class Expense(Base):
    __tablename__ = "expenses"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    raw_text: Mapped[str] = mapped_column(Text)
    place: Mapped[str | None] = mapped_column(String)
    item: Mapped[str | None] = mapped_column(String)
    is_harmful: Mapped[bool] = mapped_column(Boolean, default=False)
    llm_confidence: Mapped[float] = mapped_column(Float)

    user: Mapped["User"] = relationship(back_populates="expenses")
    category: Mapped["Category"] = relationship(back_populates="expenses")
