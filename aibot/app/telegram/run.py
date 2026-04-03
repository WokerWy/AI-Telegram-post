import asyncio
from aiogram import Dispatcher
from app.telegram.client import bot
from app.telegram.handlers import router


async def main():
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
