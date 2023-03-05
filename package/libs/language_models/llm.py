import asyncio
from typing import Any, Generator, List, Tuple
import openai
import os
from dotenv import load_dotenv
import aiohttp
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import GPT2TokenizerFast
import numpy as np

load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")
openai.api_key = api_key

gpt2_tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
def count_tokens(text: str) -> int:
    return len(gpt2_tokenizer.encode(text))

prices = {
    # All prices are per 1k tokens
    "fine-tune-train": {
        "davinci": 0.03,
        "curie": 0.03,
        "babbage": 0.0006,
        "ada": 0.0004,
    },
    "completion": {
        "davinci": 0.02,
        "curie": 0.002,
        "babbage": 0.0005,
        "ada": 0.0004,
    },
    "fine-tune-completion": {
        "davinci": 0.12,
        "curie": 0.012,
        "babbage": 0.0024,
        "ada": 0.0016,
    },
    "embedding": {
        "ada": 0.0004
    }
}

def get_price(text: str, model: str="davinci", task: str="completion") -> float:
    return count_tokens(text) * prices[task][model] / 1000

class LLM:
    def complete(self, prompt: str, **kwargs):
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
    
    def complete(self, prompt: str, **kwargs):
        args = { "max_tokens": 100 } | kwargs
        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids
        generated_ids = self.model.generate(input_ids, max_length=args["max_tokens"])
        return self.tokenizer.decode(generated_ids[0], skip_special_tokens=True)

class OpenAI(LLM):
    completion_count: int = 0
    default_model: str

    def __init__(self, model: str="text-davinci-003"):
        self.default_model = model

    def stream_chat(self, messages, **kwargs) -> Generator[Any | list | dict, None, None] | Any | list | dict:
        self.completion_count += 1
        args = { "max_tokens": 512, "temperature": 0.5, "top_p": 1, "frequency_penalty": 0, "presence_penalty": 0 } | kwargs
        args["stream"] = True
        args["model"] = "gpt-3.5-turbo"

        for chunk in openai.ChatCompletion.create(
            messages=messages,
            **args,
        ):  
            print(chunk.choices[0])
            if "content" in chunk.choices[0].delta:
                yield chunk.choices[0].delta.content
            else:
                continue

    def stream_complete(self, prompt: str, **kwargs) -> Generator[Any | list | dict, None, None] | Any | list | dict:
        self.completion_count += 1
        args = { "model": self.default_model, "max_tokens": 512, "temperature": 0.5, "top_p": 1, "frequency_penalty": 0, "presence_penalty": 0, "suffix": None } | kwargs
        args["stream"] = True

        if args["model"] == "gpt-3.5-turbo":
            generator = openai.ChatCompletion.create(
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                **args,
            )
            for chunk in generator:
                yield chunk.choices[0].message.content
        else:
            generator = openai.Completion.create(
                prompt=prompt,
                **args,
            )
            for chunk in generator:
                yield chunk.choices[0].text

    def complete(self, prompt: str, **kwargs) -> str:
        self.completion_count += 1
        args = { "model": self.default_model, "max_tokens": 512, "temperature": 0.5, "top_p": 1, "frequency_penalty": 0, "presence_penalty": 0, "suffix": None, "stream": False } | kwargs
        
        if args["model"] == "gpt-3.5-turbo":
            return openai.ChatCompletion.create(
                model=args["model"],
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                **args,
            ).choices[0].message.content
        else:
            return openai.Completion.create(
                prompt=prompt,
                **args,
            ).choices[0].text

    def embed(self, input: List[str] | str) -> List[np.ndarray]:
        resps = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=input,
        )["data"]
        return [np.array(resp["embedding"]) for resp in resps]

    def single_embed(self, input: str) -> np.ndarray:
        return self.embed([input])[0]

    def edit(self, inp: str, instruction: str) -> str:
        try:
            resp = openai.Edit.create(
                input=inp,
                instruction=instruction,
                model='text-davinci-edit-001'
            ).choices[0].text
            return resp
        except Exception as e:
            print("OpenAI error:", e)
            raise e

    def parallel_edit(self, inputs: list[str], instructions: list[str] | str, **kwargs) -> list[str]:
        args = { "temperature": 0.5, "top_p": 1 } | kwargs
        args['model'] = 'text-davinci-edit-001'
        async def fn():
            async with aiohttp.ClientSession() as session:
                tasks = []

                async def get(input, instruction):
                    async with session.post("https://api.openai.com/v1/edits", headers={
                        "Content-Type": "application/json",
                        "Authorization": "Bearer " + api_key
                    }, json={"model": args["model"], "input": input, "instruction": instruction, "temperature": args["temperature"], "max_tokens": args["max_tokens"], "suffix": args["suffix"]}) as resp:
                        json = await resp.json()
                        if "error" in json:
                            print("ERROR IN GPT-3 RESPONSE: ", json)
                            return None
                        return json["choices"][0]["text"]

                for i in range(len(inputs)):
                    tasks.append(get(inputs[i], instructions[i] if isinstance(instructions, list) else instructions))
                
                return await asyncio.gather(*tasks)

        return asyncio.run(fn())

    def parallel_complete(self, prompts: list[str], suffixes: list[str]| None=None, **kwargs) -> list[str]:
        self.completion_count += len(prompts)
        args = { "model": self.default_model, "max_tokens": 512, "temperature": 0.5, "top_p": 1, "frequency_penalty": 0, "presence_penalty": 0 } | kwargs
        async def fn():
            async with aiohttp.ClientSession() as session:
                tasks = []

                async def get(prompt, suffix):
                    async with session.post("https://api.openai.com/v1/completions", headers={
                        "Content-Type": "application/json",
                        "Authorization": "Bearer " + api_key
                    }, json={"model": args["model"], "prompt": prompt, "temperature": args["temperature"], "max_tokens": args["max_tokens"], "suffix": suffix}) as resp:
                        json = await resp.json()
                        if "error" in json:
                            print("ERROR IN GPT-3 RESPONSE: ", json)
                            return None
                        return json["choices"][0]["text"]
                
                for i in range(len(prompts)):
                    tasks.append(asyncio.ensure_future(get(prompts[i], suffixes[i] if suffixes else None)))
                
                return await asyncio.gather(*tasks)
        
        return asyncio.run(fn())