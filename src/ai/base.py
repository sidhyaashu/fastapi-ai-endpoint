from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Tuple
from src.schema import Message, ModelParameters, TokenUsage

class APIlatform(ABC):
    
    @abstractmethod
    async def chat(
        self,
        messages: List[Message],
        parameters: ModelParameters,
        system_prompt: str,
        json_mode: bool = False,
    ) -> Tuple[str, TokenUsage]:
        """
        Sends a list of messages to the AI and returns the response text and token usage.
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

    @abstractmethod
    def count_tokens(self, messages: List[Message]) -> int:
        """
        Counts the number of tokens in a list of messages.
        """
        pass
