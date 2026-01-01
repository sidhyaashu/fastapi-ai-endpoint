from typing import AsyncGenerator, List
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

from src.ai.base import APIlatform
from src.schema import Message, ModelParameters


class Gemini(APIlatform):
    def __init__(self, api_key: str, model_name: str, system_prompt: str = None):
        self.api_key = api_key
        self.system_prompt = system_prompt
        self.model_name = model_name
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            self.model_name,
            system_instruction=self.system_prompt
        )

    async def chat(
        self,
        messages: List[Message],
        parameters: ModelParameters,
        system_prompt_override: str = None,
        json_mode: bool = False, # Gemini does not have a dedicated JSON mode via a simple flag
    ) -> str:
        
        # Override the default system prompt if a new one is provided
        model = self._get_model_with_system_prompt(system_prompt_override)
        
        # Adapt messages to Gemini's expected format
        gemini_messages = [{"role": m.role, "parts": [m.content]} for m in messages]

        generation_config = self._get_generation_config(parameters, json_mode)

        response = await model.generate_content_async(
            gemini_messages,
            generation_config=generation_config,
        )
        return response.text

    async def stream_chat(
        self,
        messages: List[Message],
        parameters: ModelParameters,
        system_prompt_override: str = None,
        json_mode: bool = False,
    ) -> AsyncGenerator[str, None]:

        model = self._get_model_with_system_prompt(system_prompt_override)
        gemini_messages = [{"role": m.role, "parts": [m.content]} for m in messages]
        generation_config = self._get_generation_config(parameters, json_mode)

        stream = await model.generate_content_async(
            gemini_messages,
            stream=True,
            generation_config=generation_config,
        )
        async for chunk in stream:
            yield chunk.text

    def _get_model_with_system_prompt(self, system_prompt_override: str = None) -> genai.GenerativeModel:
        """Returns the correct model instance based on whether a system prompt override is present."""
        if system_prompt_override:
            return genai.GenerativeModel(
                self.model_name,
                system_instruction=system_prompt_override,
            )
        return self.model

    def _get_generation_config(self, parameters: ModelParameters, json_mode: bool) -> GenerationConfig:
        """Creates the GenerationConfig for the Gemini API call."""
        config_dict = {}
        if parameters:
            if parameters.temperature is not None:
                config_dict["temperature"] = parameters.temperature
            if parameters.max_tokens is not None:
                config_dict["max_output_tokens"] = parameters.max_tokens

        if json_mode:
            config_dict["response_mime_type"] = "application/json"

        return GenerationConfig(**config_dict)
