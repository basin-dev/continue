from typing import Any, Callable, Dict, List, Tuple
from ..models.main import FileEdit, EditDiff, Traceback, AbstractModel
from ..models.filesystem import FileSystem, RangeInFile
from abc import ABC, abstractmethod
from pydantic import BaseModel, root_validator
import subprocess
from .traceback_parsers import parse_python_traceback
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

class ActionParams:
    filesystem: FileSystem
    llm: LLM

    def __init__(self, filesystem: FileSystem, llm: LLM):
        self.filesystem = filesystem
        self.llm = llm

class Action(AbstractModel):
    @abstractmethod
    def run(self, params: ActionParams) -> List[FileEdit]:
        raise NotImplementedError()

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

class Agent:
    history: History
    llm: LLM
    filesystem: FileSystem
    router: Router

    # Agent should maybe have locks

    def __init__(self, llm: LLM, validators: List[Validator], filesystem: FileSystem, router: Router, max_runs_per_validator: int = 1):
        self.llm = llm
        self.validators = validators
        self.filesystem = filesystem
        self.router = router
        self.max_runs_per_validator = max_runs_per_validator
        self.history = History(states=[], filesystem=filesystem)

    def _get_action_params(self) -> ActionParams:
        return ActionParams(
            llm=self.llm,
            filesystem=self.filesystem
        )
    
    def _apply_action(self, action: Action) -> List[EditDiff]:
        edits = action.run(self._get_action_params())
        diffs = []
        for edit in edits:
            # Should replace this with something inherent to EditDiff, this is slow. Also, do you want to use real diffs, or this, which is better for making suggestions?
            if edit.replacement == self.filesystem.read_range_in_file(RangeInFile(filepath=edit.filepath, range=edit.range)):
                continue
            diffs.append(self.filesystem.apply_file_edit(edit))
        return diffs

    def act(self, action: Action):
        diffs = self._apply_action(action)
        self.history.add(HistoryState(action_taken=action, diffs=diffs))

    def _rerun_current_action(self):
        idx_in_history = self.history.current_state_idx

        diffs = self._apply_action(self.history.states[idx_in_history].action_taken)
        self.history.states[idx_in_history].diffs = diffs

    def rerun_from_state(self, idx_in_history: int):
        # To do this, you need to know the actions that were taken.
        # An interesting thing is if you run again and don't get the same errors.
        # So you need to know which actions were in response to fixing validation errors.

        # This is bad...there's too much intimate understanding between Agent and History
        self.history.revert_to_state(idx_in_history)

        for i in range(idx_in_history, len(self.history.states)):
            self._rerun_current_action()
            self.history.current_state_idx = i

    # Shouldn't it be able to run and check recursively? And keep track of the global number of loops?
    def run_and_check(self, action: Action) -> bool:
        """Run the agent, returning whether successful."""
        self.act(action)
        success = self.fix_validators()
        return success
    
    def fix_validator(self, validator: Validator) -> bool:
        i = 0
        passed = False
        while i < self.max_runs_per_validator and not passed:
            passed, artifact = validator.run(self.filesystem)
            print("------------- Validator: ", passed, artifact)

            if passed:
                passed = True
            else:
                # Run the action that can fix this artifact
                next_action = self.router.next_action([artifact])
                
                if next_action is None:
                    return False
                
                self._run_action(next_action)

                # Then the validator is rerun --^

        return passed

    def fix_validators(self) -> bool:
        """Attempt to run and fix all validators, returning whether successful."""
        # Should probably also return WHY it was unsuccessful
        a_validator_failed = False
        for validator in self.validators:
            passed = self.fix_validator(validator)
            if not passed:
                a_validator_failed = True
                break

        return a_validator_failed
    
    def print_history(self):
        for diff in self.history:
            print("---------------------------------")
            print(f"File: {diff.edit.filepath}\n{diff.edit.replacement}")
            print("---------------------------------")