#!/usr/bin/env python3
# filepath: c:\Users\Jaro\Desktop\3rd-devs\thread-py\openai_service.py
from openai import OpenAI
from typing import Union, Dict, List, Any, AsyncIterable
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class OpenAIService:
    def __init__(self):
        self.openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    def completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "gpt-4", 
        stream: bool = False
    ) -> Union[Dict[str, Any], Any]:
        try:
            chat_completion = self.openai.chat.completions.create(
                messages=messages,
                model=model,
                stream=stream
            )
            
            if stream:
                return chat_completion  # AsyncIterable of chunks
            else:
                return chat_completion  # ChatCompletion object
        except Exception as error:
            print(f"Error in OpenAI completion: {error}")
            raise error
                
