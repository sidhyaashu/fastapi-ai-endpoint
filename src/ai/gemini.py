from src.ai.base import APIlatform
import google.generativeai as genai


class Gemini(APIlatform):
    def __init__(self,api_key:str, model_name:str = "gemini-1.5-flash", system_prompt:str = None):
        self.api_key = api_key
        self.system_prompt = system_prompt
        self.model_name = model_name
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name, system_instruction=self.system_prompt)
        
        
    async def chat(self, prompt:str)->str:
        response = await self.model.generate_content_async(prompt)
        return response.text
