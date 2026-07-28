import os
import asyncio
import logging
from dotenv import load_dotenv, find_dotenv
from aiogram import Bot, Dispatcher
from bot.handlers import router
from bot.middlewares.translator import TranslatorMiddleware

load_dotenv(find_dotenv(usecwd=True))

BOT_TOKEN = os.getenv("BOT_TOKEN")


async def main():
    logging.basicConfig(level=logging.INFO)
    if not BOT_TOKEN:
        print("BOT_TOKEN is not set in environment.")
        return

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Register translator middleware for messages and callback queries
    translator_middleware = TranslatorMiddleware()
    dp.message.middleware(translator_middleware)
    dp.callback_query.middleware(translator_middleware)

    dp.include_router(router)

    print("Telegram Bot starting polling with full i18n translation support...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
