import json
import asyncio
from gigachat import GigaChat

from core.config import settings
from app.core.llm.schemas import ExpenseParseResult
from app.core.llm.prompts import CATEGORIZE_EXPENSE_PROMPT


async def categorize_expense(
    user_text: str, existing_categories: list[str]
) -> ExpenseParseResult:
    prompt = CATEGORIZE_EXPENSE_PROMPT.format(
        existing_categories=existing_categories, user_text=user_text
    )

    async with GigaChat(
        credentials=settings.gigachat.credentials,
        scope=settings.gigachat.scope,
        ca_bundle_file=settings.gigachat.ca_bundle_file,
    ) as giga:
        response = await giga.achat(prompt)

    raw_content = response.choices[0].message.content
    data = json.loads(raw_content)
    result = ExpenseParseResult(**data)
    return result
