from datetime import datetime
from typing import List, Dict
import uuid


class TelegramParser:
    """
    MOCK Telegram parser.
    Реальный Telethon будет подключён позже.
    """

    async def parse_channel(self, channel: str, limit: int = 5) -> List[Dict]:
        results = []

        for i in range(limit):
            results.append({
                "id": str(uuid.uuid4()),
                "title": f"Telegram post {i + 1} from {channel}",
                "summary": f"Mock summary of telegram post {i + 1}",
                "raw_text": f"Mock raw text of post {i + 1}",
                "source": channel,
                "url": f"https://t.me/{channel}/{i + 1}",
                "published_at": datetime.utcnow()
            })

        return results
