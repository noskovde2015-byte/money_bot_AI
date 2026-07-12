import asyncio
from aiogram import Bot
from app.bot.dispatcher import create_dispatcher
from app.core.config import settings


async def main():
    bot = Bot(token=settings.bot.token)
    dp = create_dispatcher()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
