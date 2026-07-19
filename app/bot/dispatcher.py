from aiogram import Dispatcher
from app.bot.middlewares.user_middleware import UserMiddleware
from app.bot.handlers.start import router as start_router
from app.bot.handlers.income import router as income_router
from app.bot.handlers.expense import router as expense_router
from app.bot.handlers.report import router as report_router


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.message.middleware(UserMiddleware())
    dp.include_router(start_router)
    dp.include_router(income_router)
    dp.include_router(expense_router)
    dp.include_router(report_router)
    return dp
