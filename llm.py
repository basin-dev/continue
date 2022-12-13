import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

class LLM:
    def complete(self, prompt: str,
            temp=0.5,
            max_tokens=100,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None):
        """Return the completion of the text with the given temperature."""
        raise NotImplementedError
    
    def fine_tune(self, pairs: list):
        """Fine tune the model on the given prompt/completion pairs."""
        raise NotImplementedError

class OpenAI(LLM):
    def __init__(self, engine: str = "davinci"):
        self.engine = engine
        
    def complete(self, prompt: str,
            temp=0.5,
            max_tokens=100,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None):
        return openai.Completion.create(
            engine=self.engine,
            prompt=prompt,
            temperature=temp,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop
        ).choices[0].text