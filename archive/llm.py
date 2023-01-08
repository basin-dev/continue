import asyncio
import openai
import os
from dotenv import load_dotenv
import aiohttp
from transformers import AutoTokenizer, AutoModelForCausalLM

load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")
openai.api_key = api_key

class LLM:
    def complete(self, prompt: str,
            temp=0.5,
            max_tokens=100,
            stop=None):
        """Return the completion of the text with the given temperature."""
        raise NotImplementedError
    
    def fine_tune(self, pairs: list):
        """Fine tune the model on the given prompt/completion pairs."""
        raise NotImplementedError

class HuggingFace(LLM):
    def __init__(self, model_path: str = "Salesforce/codegen-2B-mono"):
        self.model_path = model_path
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(model_path)
    
    def complete(self, prompt: str,
            temp=0.5,
            max_tokens=100,
            stop=None):
        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids
        generated_ids = self.model.generate(input_ids, max_length=max_tokens)
        return self.tokenizer.decode(generated_ids[0], skip_special_tokens=True)

class OpenAI(LLM):
    def __init__(self, engine: str = "davinci"):
        self.engine = engine
        
    def complete(self, prompt: str,
            temp=0.5,
            max_tokens=100,
            stop=None):
        return openai.Completion.create(
            engine=self.engine,
            prompt=prompt,
            temperature=temp,
            max_tokens=max_tokens,
            stop=stop
        ).choices[0].text

    def parallel_complete(self, prompts: list[str],
            temp=0.5,
            max_tokens=100,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None) -> list[str]:
        async def fn():
            async with aiohttp.ClientSession() as session:
                tasks = []

                async def get(prompt):
                    async with session.post("https://api.openai.com/v1/completions", headers={
                        "Content-Type": "application/json",
                        "Authorization": "Bearer " + api_key
                    }, json={"model": self.engine, "prompt": prompt, "temperature": temp, "max_tokens": max_tokens}) as resp:
                        json = await resp.json()
                        if "error" in json:
                            print("ERROR IN GPT-3 RESPONSE: ", json)
                            # GPT-3 rate limit reached, just return no for now
                            return None
                        return json["choices"][0]["text"]
                
                for i in range(len(prompts)):
                    tasks.append(asyncio.ensure_future(get(prompts[i])))
                
                return await asyncio.gather(*tasks)
        
        return asyncio.run(fn())