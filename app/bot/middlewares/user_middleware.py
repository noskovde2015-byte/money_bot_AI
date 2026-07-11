# app/bot/middlewares/user_middleware.py

from typing import Callable, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import Message

from sqlalchemy import select
from app.db.user import User
from app.db.db_helper import db_helper


class UserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        async with db_helper.session_factory() as session:
            stmt = select(User).where(User.telegram_id == event.from_user.id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user is None:
                user = User(
                    telegram_id=event.from_user.id,
                    username=event.from_user.username,
                    full_name=event.from_user.full_name,
                )
                session.add(user)
                await session.commit()

            data["user"] = user
            data["session"] = session

            return await handler(event, data)
