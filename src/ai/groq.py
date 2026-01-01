from src.ai.base import APIlatform
from groq import AsyncGroq


class Groq(APIlatform):
    def __init__(self, api_key: str, model_name: str = "llama3-8b-8192", system_prompt: str = None):
        self.api_key = api_key
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.client = AsyncGroq(api_key=self.api_key)

    async def chat(self, prompt: str) -> str:
        messages = [{"role": "user", "content": prompt}]
        if self.system_prompt:
            messages.insert(0, {"role": "system", "content": self.system_prompt})

        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages
        )
        return response.choices[0].message.content
