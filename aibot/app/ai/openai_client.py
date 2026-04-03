import httpx
from app.config import settings


class OpenAIClient:
    def __init__(self):
        self.api_key = settings.openai_api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    async def generate(self, prompt: str) -> str:
        #  SAFE MOCK MODE
        if not self.api_key or self.api_key.lower().startswith("mock"):
            return (
                "🤖 MOCK AI POST\n\n"
                "This is a generated Telegram post (mock mode).\n\n"
                "👉 Follow the channel for updates!"
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You generate Telegram posts."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                self.base_url,
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

        return data["choices"][0]["message"]["content"]
