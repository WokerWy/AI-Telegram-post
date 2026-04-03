from app.telegram.bot import TelegramBot


class TelegramSender:
    def __init__(self):
        self.bot = TelegramBot()

    async def send_post(self, text: str):
        await self.bot.send_message(text)
