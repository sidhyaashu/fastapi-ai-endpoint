from src.ai.base import APIlatform
from google import genai


class Gemini(APIlatform):
    def __init__(self,api_key:str, model_name:str = "gemini-2.0-flash", system_prompt:str = None):
        """
        Initializes the Gemini platform.

        Args:
            api_key (str): Your Google AI API key.
            model_name (str, optional): The name of the model to use. Defaults to "gemini-pro".
            system_prompt (str, optional): The system prompt to use for the model. Defaults to None.
        """
        self.api_key = api_key
        self.system_prompt = system_prompt
        self.model_name = model_name
        self.client = genai.Client(api_key=self.api_key)
        
        
    def chat(self, prompt:str)->str:
        if self.system_prompt:
            prompt = f"{self.system_prompt}\n\n{prompt}"
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        
        return response.text
        
        