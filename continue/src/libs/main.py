from typing import Any, Callable, List, Tuple
from ..models.main import FileEdit, EditDiff, AbstractModel
from ..models.filesystem import FileSystem
from abc import abstractmethod
from pydantic import BaseModel
from .actions.llm.main import LLM

# Edits must be atomic, do we ever want multiple agents working on the code at once?? This is tough because hard to know when things interact with each other.
# Source -> subscriber -> agent -> check policy, ask if needed -> perform edit -> record edit in workflow -> redo the action

# Either you start because there's an error, or because you want to add a feature.
# If the latter, you might define how you want to test it. If the former, also need to know, but it's probably running the program.

# There should be a list of goals: 1. get it to compile, 2. get it to run
# You continue fixing until you can move on to the next goal.

# Need to be able to gracefully fail when the agent tries to access something it isn't allowed to


# Do something > validate > artifact if failed > depending on what artifacts you have, router to map to actions > first usually are enricher actions (give an additional artifact) > then real action (generates a FileEdit) > apply edit > repeat validator
# So...important concepts are
# Agent, Validator, Action, Artifact, Enricher, Router (instead of hook)

# Actions should specify the required artifacts, then you attempt to find a path through enrichers that gives you the required artifacts
# The point of finding the path is that you might not always have access to all of the enrichers? Like if you don't/can't run a LSP
# But this might be too narrow a framework, because you might just dynamically need to decide what extra information is needed.
# For example, you only create the call graph if you have an assertion error traceback.

class Artifact(BaseModel):
    artifact_type: str
    data: Any

# Enrichers!!!!
# This is what collects the debug context. You might start with a traceback, but then you run deterministic tools to enrich.
# Is an enricher different from an action? An enricher COULD just be an action, but it might be easier to read if separate.

Enricher = Callable[[Artifact], Artifact]

class Validator(AbstractModel):
    @abstractmethod
    def run(self, fs: FileSystem) -> Tuple[bool, Artifact]:
        raise NotImplementedError

class Router(AbstractModel):
    @abstractmethod
    def next_action(self, artifacts: List[Artifact]) -> Action | None: # Might do better than None by having a special Action type to represent being done and successful
        raise NotImplementedError()

class HistoryState(BaseModel):
    action_taken: Action
    diffs: List[EditDiff]

class History(BaseModel):
    states: List[HistoryState]
    current_state_idx: int = 0
    filesystem: FileSystem

    def add(self, state: HistoryState):
        if self.current_state_idx < len(self.states) - 1:
            self.states = self.states[:self.current_state_idx + 1]

        self.states.append(state)
        self.current_state_idx += 1

    def revert_to_state(self, idx_in_history: int):
        for i in range(len(self.states) - 1, idx_in_history - 1, -1):
            diff = self.states[i].diff
            self.filesystem.reverse_file_edit(diff)
            self.states.pop()

        self.current_state_idx = idx_in_history