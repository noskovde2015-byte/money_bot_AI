from functools import lru_cache

from aiogram import Bot, Dispatcher

from app.core.config import settings
from app.bot.dispatcher import create_dispatcher


@lru_cache
def get_bot() -> Bot:
    return Bot(token=settings.bot.token)


@lru_cache
def get_dispatcher() -> Dispatcher:
    return create_dispatcher()
