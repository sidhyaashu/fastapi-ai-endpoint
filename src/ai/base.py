from abc import ABC, abstractmethod

class APIlatform(ABC):
    
    @abstractmethod
    def chat(self, prompt:str):
        """
        Sends a prompt to the AI and return the response text

        """

        pass