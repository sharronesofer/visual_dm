class GPTRequest:
    def __init__(self, model="gpt-4", temperature=0.7, max_tokens=150):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def call(self, system_prompt, user_prompt):
        """
        Send the prompt to OpenAI and return the response.
        """
        pass
