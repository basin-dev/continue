from .libs.steps.main import RunCodeStep
from .libs.policy import DemoPolicy
from .libs.llm.openai import OpenAI
from .libs.core import Agent
import os
from dotenv import load_dotenv
from typer import Typer

app = Typer()

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

@app.command()
def main(cmd: str="python3 /Users/natesesti/Desktop/continue/extension/examples/python/main.py"):
    agent = Agent(llm=OpenAI(api_key=openai_api_key), policy=DemoPolicy(cmd=cmd))
    agent.run_from_step(RunCodeStep(cmd=cmd))

if __name__ == "__main__":
    app()
