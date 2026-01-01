from typing import AsyncGenerator, List, Dict, Any
from anthropic import AsyncAnthropic
from src.ai.base import APIlatform
from src.schema import Message, ModelParameters


class Anthropic(APIlatform):
    def __init__(self, api_key: str, model_name: str, system_prompt: str = None):
        self.api_key = api_key
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.client = AsyncAnthropic(api_key=self.api_key)

    async def chat(
        self,
        messages: List[Message],
        parameters: ModelParameters,
        system_prompt_override: str = None,
        json_mode: bool = False, # Anthropic does not support a dedicated JSON mode
    ) -> str:

        api_messages = [msg.model_dump() for msg in messages]
        api_parameters = self._prepare_parameters(parameters)
        final_system_prompt = system_prompt_override if system_prompt_override is not None else self.system_prompt

        response = await self.client.messages.create(
            model=self.model_name,
            messages=api_messages,
            system=final_system_prompt,
            **api_parameters,
        )
        return response.content[0].text

    async def stream_chat(
        self,
        messages: List[Message],
        parameters: ModelParameters,
        system_prompt_override: str = None,
        json_mode: bool = False,
    ) -> AsyncGenerator[str, None]:

        api_messages = [msg.model_dump() for msg in messages]
        api_parameters = self._prepare_parameters(parameters)
        final_system_prompt = system_prompt_override if system_prompt_override is not None else self.system_prompt

        async with self.client.messages.stream(
            model=self.model_name,
            messages=api_messages,
            system=final_system_prompt,
            **api_parameters,
        ) as stream:
            async for text in stream.text_stream:
                yield text

    def _prepare_parameters(self, parameters: ModelParameters) -> Dict[str, Any]:
        """Prepares the parameters dictionary for the Anthropic API."""
        api_parameters = {}
        # Anthropic requires max_tokens
        api_parameters["max_tokens"] = parameters.max_tokens if parameters and parameters.max_tokens else 1024

        if parameters:
            if parameters.temperature is not None:
                api_parameters["temperature"] = parameters.temperature

        return api_parameters
