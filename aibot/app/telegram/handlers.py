from aiogram import Router
from aiogram.types import Message
from app.telegram.publisher import TelegramPublisher

router = Router()
publisher = TelegramPublisher()


@router.message(commands=["generate"])
async def generate(message: Message):
    await publisher.send_message(
        "🚀 AI-generated post"
    )
    await message.answer("✅ Post sent to channel")

@router.message(commands=["ping"])
async def ping(message: Message):
    await message.answer("🏓 Pong! Bot is alive")