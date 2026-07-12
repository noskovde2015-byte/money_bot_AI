from aiogram import Dispatcher
from app.bot.middlewares.user_middleware import UserMiddleware
from app.bot.handlers.start import router as start_router


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.message.middleware(UserMiddleware())
    dp.include_router(start_router)
    return dp
