from typing import AsyncGenerator, List, Dict, Any
from openai import AsyncOpenAI
from src.ai.base import APIlatform
from src.schema import Message, ModelParameters


class OpenAI(APIlatform):
    def __init__(self, api_key: str, model_name: str, system_prompt: str = None):
        self.api_key = api_key
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def chat(
        self,
        messages: List[Message],
        parameters: ModelParameters,
        system_prompt_override: str = None,
        json_mode: bool = False,
    ) -> str:

        api_messages = self._prepare_messages(messages, system_prompt_override)
        api_parameters = self._prepare_parameters(parameters, json_mode)

        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=api_messages,
            **api_parameters,
        )
        return response.choices[0].message.content

    async def stream_chat(
        self,
        messages: List[Message],
        parameters: ModelParameters,
        system_prompt_override: str = None,
        json_mode: bool = False,
    ) -> AsyncGenerator[str, None]:

        api_messages = self._prepare_messages(messages, system_prompt_override)
        api_parameters = self._prepare_parameters(parameters, json_mode, stream=True)

        stream = await self.client.chat.completions.create(
            model=self.model_name,
            messages=api_messages,
            **api_parameters,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    def _prepare_messages(self, messages: List[Message], system_prompt_override: str = None) -> List[Dict[str, str]]:
        """Prepares the message list for the OpenAI API."""
        # Convert Pydantic models to dictionaries
        api_messages = [msg.model_dump() for msg in messages]

        # Determine the system prompt to use
        final_system_prompt = system_prompt_override if system_prompt_override is not None else self.system_prompt

        if final_system_prompt:
            api_messages.insert(0, {"role": "system", "content": final_system_prompt})

        return api_messages

    def _prepare_parameters(self, parameters: ModelParameters, json_mode: bool, stream: bool = False) -> Dict[str, Any]:
        """Prepares the parameters dictionary for the OpenAI API."""
        api_parameters = {"stream": stream}
        if parameters:
            if parameters.temperature is not None:
                api_parameters["temperature"] = parameters.temperature
            if parameters.max_tokens is not None:
                api_parameters["max_tokens"] = parameters.max_tokens

        if json_mode:
            api_parameters["response_format"] = {"type": "json_object"}

        return api_parameters
