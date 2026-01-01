from abc import ABC, abstractmethod
from typing import AsyncGenerator, List
from src.schema import Message, ModelParameters

class APIlatform(ABC):
    
    @abstractmethod
    async def chat(
        self,
        messages: List[Message],
        parameters: ModelParameters,
        system_prompt: str,
        json_mode: bool = False,
    ) -> str:
        """
        Sends a list of messages to the AI and returns the response text.
        """
        pass

    @abstractmethod
    async def stream_chat(
        self,
        messages: List[Message],
        parameters: ModelParameters,
        system_prompt: str,
        json_mode: bool = False,
    ) -> AsyncGenerator[str, None]:
        """
        Sends a list of messages to the AI and streams the response.
        """
        pass
        # This is a placeholder for the generator
        if False:
            yield
