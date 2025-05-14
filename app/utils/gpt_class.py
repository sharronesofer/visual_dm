import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class GPTClient:
    """Client for interacting with GPT models."""
    
    def __init__(self):
        """Initialize the GPT client with API key from environment."""
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4"  # Default model
        
    def generate_response(self, prompt, system_prompt=None, temperature=0.7, max_tokens=150):
        """Generate a response from GPT."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating GPT response: {e}")
            return None
    
    def set_model(self, model_name):
        """Set the GPT model to use."""
        self.model = model_name 