from .libs.main import Agent, PytestValidator, PythonTracebackValidator, Hook
from .libs.actions.main import solve_traceback_action
from .libs.actions.llm.openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

if __name__ == "__main__":
    cwd = "/Users/natesesti/Desktop/continue/extension/examples/python"

    agent = Agent(
        llm=OpenAI(api_key=openai_api_key),
        validators=[
            PythonTracebackValidator("python3 main.py", cwd=cwd),
            PytestValidator(cwd=cwd)
        ],
        hooks=[ Hook(artifact_type="traceback", action=solve_traceback_action) ]
    )