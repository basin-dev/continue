# This file contains actions that communicate with a language model.
# You might end up wanting to integrate llms more tightly because of wanting to stream, etc...

# Actually, the language model used should be a part of the agent, so the agent should be passed to the action
# Something like "run this action with this agent" instead of "have this agent run this action"

# OR are actions run within a context manager? But don't think this works through functions
import asyncio
from typing import Any, Generator, List
import openai
import aiohttp
import numpy as np
from ..llm import LLM
from pydantic import BaseModel, validator

class OpenAI(LLM):
    api_key: str
    completion_count: int = 0
    default_model: str = "text-davinci-003"

    @validator("api_key", pre=True, always=True)
    def validate_api_key(cls, v):
        openai.api_key = v
        return v

    def stream_chat(self, messages, **kwargs) -> Generator[Any | list | dict, None, None] | Any | list | dict:
        self.completion_count += 1
        args = { "max_tokens": 512, "temperature": 0.5, "top_p": 1, "frequency_penalty": 0, "presence_penalty": 0 } | kwargs
        args["stream"] = True
        args["model"] = "gpt-3.5-turbo"

        for chunk in openai.ChatCompletion.create(
            messages=messages,
            **args,
        ):  
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
                        "Authorization": "Bearer " + self.api_key
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
                        "Authorization": "Bearer " + self.api_key
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