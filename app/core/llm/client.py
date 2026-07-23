import json
import asyncio
from gigachat import GigaChat

from app.core.config import settings
from app.core.llm.schemas import ExpenseParseResult, IncomeParseResult
from app.core.llm.prompts import (
    CATEGORIZE_EXPENSE_PROMPT,
    REPORT_INSIGHT_PROMPT,
    CATEGORIZE_INCOME_PROMPT,
)


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


async def generate_report_insight(report_data: dict) -> str:
    if report_data["change_percent"] is not None:
        change_info = f"{report_data['change_percent']:.1f}%"
    else:
        change_info = "нет данных за прошлый месяц для сравнения"

    prompt = REPORT_INSIGHT_PROMPT.format(
        current_expenses=report_data["current_expenses"],
        current_incomes=report_data["current_incomes"],
        by_category=report_data["by_category"],
        harmful_total=report_data["harmful_total"],
        change_info=change_info,
    )

    async with GigaChat(
        credentials=settings.gigachat.credentials,
        scope=settings.gigachat.scope,
        ca_bundle_file=settings.gigachat.ca_bundle_file,
    ) as giga:
        response = await giga.achat(prompt)

    raw_content = response.choices[0].message.content
    return raw_content


async def categorize_income(
    user_text: str, existing_sources: list[str]
) -> IncomeParseResult:
    prompt = CATEGORIZE_INCOME_PROMPT.format(
        user_text=user_text, existing_sources=existing_sources
    )

    async with GigaChat(
        credentials=settings.gigachat.credentials,
        scope=settings.gigachat.scope,
        ca_bundle_file=settings.gigachat.ca_bundle_file,
    ) as giga:
        response = await giga.achat(prompt)

    raw_content = response.choices[0].message.content
    data = json.loads(raw_content)
    result = IncomeParseResult(**data)
    return result
