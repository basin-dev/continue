from .libs.agent import DemoAgent
import os
from dotenv import load_dotenv
from typer import Typer

app = Typer()

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

@app.command()
def main(cmd: str="python3 /Users/natesesti/Desktop/continue/extension/examples/python/main.py"):
    agent = DemoAgent(cmd)
    # agent.print_history()

if __name__ == "__main__":
    app()

# Instead of hooks, potentially have routers: functions that take a list of artifacts and choose a next action to address them.
# Routers maybe also should be stateful
# What's a better name? It's all about deciding what to do next, just like a human would
# In the end though, the real person should have ability to see the options at each point, and to reselect. These depend on a mapping of artifact requirements to actions, OR an action should be a class that also has a function to determine whether the requirements are met.
# Planner?

# If the agent is to be able to go down multiple routes, it should fully be a DAG (or tree, if you want to make the assumption that convergence is unlikely and checking is taxing)
# So then there should be a History class.
