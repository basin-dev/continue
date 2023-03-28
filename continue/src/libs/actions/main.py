from ...models.main import FileEdit, Traceback
from ...models.filesystem import FileSystem
from ..main import Agent

# Annoying to pass around the filesystem the whole time
# There should be an entire langauge-agnostic pipeline through the 1. running command, 2. parsing traceback, 3. generating edit
def solve_traceback_action(agent: Agent, traceback: Traceback) -> FileEdit:
    

# How to make actions composable??