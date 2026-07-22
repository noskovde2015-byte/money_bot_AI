from contextlib import asynccontextmanager
from app.core.config import settings
from fastapi import FastAPI
from app.api.dependencies import get_bot


@asynccontextmanager
async def lifespan(app: FastAPI):
    bot = get_bot()
    await bot.set_webhook(url=settings.webhook.url)

    yield

    await bot.delete_webhook()
    await bot.session.close()
