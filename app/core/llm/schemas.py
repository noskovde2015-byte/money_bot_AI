from pydantic import BaseModel, Field


class ExpenseParseResult(BaseModel):
    amount: float | None = Field(description="Сумма траты в рублях")
    category: str | None = Field(description="Название категории")
    is_new_category: bool = Field(
        description="True, если категория не входит в существующий список"
    )
    place: str | None = Field(default=None, description="Место покупки")
    item: str | None = Field(default=None, description="Что купили")
    is_harmful: bool = Field(default=False, description="Вредная ли трата для бюджета")
    confidence: float = Field(ge=0, le=1, description="Уверенность модели в разборе")
