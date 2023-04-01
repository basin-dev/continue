from typing import List

from .libs.actions.main import SolveTracebackAction
from .libs.main import Action, Agent, Artifact, Router, BasicRouter
from .libs.validators.python import PythonTracebackValidator, PytestValidator
from .libs.actions.llm.openai import OpenAI
from .models.filesystem import RealFileSystem
import os
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

if __name__ == "__main__":
    cwd = "/Users/natesesti/Desktop/continue/extension/examples/python"
    filesystem = RealFileSystem() # FileSystem should probably be where permissions are ensured
    tb_validator = PythonTracebackValidator("python3 main.py", cwd)

    agent = Agent(
        llm=OpenAI(api_key=openai_api_key),
        validators=[
            tb_validator,
            PytestValidator(cwd=cwd)
        ],
        router=BasicRouter(),
        filesystem=filesystem
    )

    agent.fix_validator(tb_validator) # "Fix" isn't the right word: something more like address
    agent.print_history()

# Instead of hooks, potentially have routers: functions that take a list of artifacts and choose a next action to address them.
# Routers maybe also should be stateful
# What's a better name? It's all about deciding what to do next, just like a human would
# In the end though, the real person should have ability to see the options at each point, and to reselect. These depend on a mapping of artifact requirements to actions, OR an action should be a class that also has a function to determine whether the requirements are met.
# Planner?

# If the agent is to be able to go down multiple routes, it should fully be a DAG (or tree, if you want to make the assumption that convergence is unlikely and checking is taxing)
# So then there should be a History class.
