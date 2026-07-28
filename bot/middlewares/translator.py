from typing import Any, Awaitable, Callable, Dict, Literal, Optional, Protocol
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
import redis.asyncio as redis

from bot.utils.translations import load_translations
from common import get_redis_client


class Translate(Protocol):
    async def __call__(
        self, key: str, lang: Optional[str] = None, user_id: Optional[int] = None, **kwargs: Any
    ) -> str: ...

    async def set_lang(self, lang: Literal["uz", "ru", "en"]) -> None: ...

    async def get_lang() -> str: ...


class Translator:
    def __init__(
        self, translations: dict[str, dict[str, str]], redis: redis.Redis, user_id: int
    ):
        self.translations = translations
        self.redis = redis
        self.user_id = user_id

    async def set_lang(self, lang: Literal["uz", "ru", "en"]):
        await self.redis.set(f"lang:{self.user_id}", lang)

    async def get_lang() -> str:
        val = await self.redis.get(f"lang:{self.user_id}")
        return val or "uz"

    async def __call__(
        self, key: str, lang: Optional[str] = None, user_id: Optional[int] = None, **kwargs: Any
    ) -> str:
        user_lang = lang

        if not user_lang and user_id is not None:
            val = await self.redis.get(f"lang:{user_id}")
            if val:
                user_lang = val

        if not user_lang and user_id is None:
            val = await self.redis.get(f"lang:{self.user_id}")
            if val:
                user_lang = val

        user_lang = user_lang or "uz"
        text = self.translations.get(user_lang, {}).get(key, key)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except Exception:
                pass
        return text


class TranslatorMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()
        self.translations = load_translations()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_id: Optional[int] = None

        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id

        if user_id:
            redis_client = get_redis_client()
            try:
                translator = Translator(self.translations, redis_client, user_id)
                data["translate"] = translator
                return await handler(event, data)
            finally:
                await redis_client.aclose()
        else:
            return await handler(event, data)
