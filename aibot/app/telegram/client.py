from aiogram import Bot
from app.config import settings
import logging

logger = logging.getLogger(__name__)

bot = Bot(token=settings.telegram_bot_token)


async def send_telegram_message(text: str, chat_id: int | None = None):
    try:
        await bot.send_message(
            chat_id=chat_id or settings.telegram_chat_id,
            text=text
        )
        logger.info("Telegram message sent")

    except Exception:
        logger.exception("Failed to send Telegram message")
        raise
