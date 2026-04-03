import asyncio
from app.telegram.bot import TelegramBot


async def main():
    bot = TelegramBot()
    await bot.send_message("✅ Telegram bot works!")


if __name__ == "__main__":
    asyncio.run(main())
