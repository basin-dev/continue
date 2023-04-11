from dotenv import load_dotenv
import os
from .core import Agent
from .llm.openai import OpenAI
from .policy import DemoPolicy
from ..models.filesystem import RealFileSystem

load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")

class DemoAgent(Agent):
    def __init__(self, cmd: str):
        policy = DemoPolicy(cmd=cmd)
        super().__init__(llm=OpenAI(api_key=api_key), filesystem=RealFileSystem(), policy=policy)