from src.ai.base import APIlatform
from anthropic import AsyncAnthropic


class Anthropic(APIlatform):
    def __init__(self, api_key: str, model_name: str = "claude-3-opus-20240229", system_prompt: str = None):
        self.api_key = api_key
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.client = AsyncAnthropic(api_key=self.api_key)

    async def chat(self, prompt: str) -> str:
        response = await self.client.messages.create(
            model=self.model_name,
            max_tokens=1024,
            system=self.system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
