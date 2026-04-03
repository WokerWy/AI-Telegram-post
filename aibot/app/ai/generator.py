from app.ai.openai_client import OpenAIClient
from app.telegram.bot import TelegramBot


class PostGenerator:
    def __init__(self):
        self.ai = OpenAIClient()
        self.telegram = TelegramBot()

    async def generate_and_send(self, prompt: str) -> str:
        text = await self.ai.generate(prompt)
        await self.telegram.send_message(text)
        return text
