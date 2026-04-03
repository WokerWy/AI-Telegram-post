import logging
import httpx
from app.config import settings

logger = logging.getLogger("telegram")

class TelegramBot:
    def __init__(self):
        self.token = settings.telegram_bot_token
        self.chat_id = settings.telegram_chat_id
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    async def send_message(self, text: str):
        logger.info("Sending message to Telegram")

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{self.base_url}/sendMessage",
                json={
                    "chat_id": self.chat_id,
                    "text": text,
                    "parse_mode": "HTML"
                }
            )

            response.raise_for_status()

        logger.info("Telegram message sent")
