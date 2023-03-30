from typing import Any, Callable, Dict, List, Tuple
from ..models.main import FileEdit, EditDiff, Traceback
from ..models.filesystem import FileSystem, RangeInFile
from abc import ABC, abstractmethod
from pydantic import BaseModel
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

class Action(ABC):
    @abstractmethod
    def run(self, params: ActionParams) -> List[FileEdit]:
        raise NotImplementedError()

# Enrichers!!!!
# This is what collects the debug context. You might start with a traceback, but then you run deterministic tools to enrich.
# Is an enricher different from an action? An enricher COULD just be an action, but it might be easier to read if separate.

Enricher = Callable[[Artifact], Artifact]

class Validator(ABC):
    @abstractmethod
    def run(self, fs: FileSystem) -> Tuple[bool, Artifact]:
        raise NotImplementedError
    
# Might want to separate the parser ("Snooper") from the thing that runs the python program and receives stdout
# And might want to separate the traceback parser, because what if they are different for different python versions or something?
class PythonTracebackValidator(Validator):
    def __init__(self, cmd: str, cwd: str):
        self.cmd = cmd
        self.cwd = cwd

    def run(self, fs: FileSystem) -> Tuple[bool, Artifact]:
        # Run the python file
        result = subprocess.run(self.cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.cwd)
        stdout = result.stdout.decode("utf-8")
        stderr = result.stderr.decode("utf-8")
        print(stdout, stderr)

        # If it fails, return the error
        tb = parse_python_traceback(stdout) or parse_python_traceback(stderr)
        if tb:
            return False, Artifact(artifact_type="traceback", data=tb)
        
        # If it succeeds, return None
        return True, None
    
# Things get weird if you have to set up an environment to run. Make this part of cmd, the class, or the agent?
# Do you want to pass some context about the traceback and where it came from?
class PytestValidator(Validator):
    def __init__(self, cwd: str):
        self.cwd = cwd

    def run(self, fs: FileSystem) -> Tuple[bool, Artifact]:
        # Run the python file
        result = subprocess.run(["pytest", "--tb=native"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.cwd)
        stdout = result.stdout.decode("utf-8")
        stderr = result.stderr.decode("utf-8")

        stdout_tb = parse_python_traceback(stdout)
        stderr_tb = parse_python_traceback(stderr)

        # If it fails, return the error
        if stdout_tb or stderr_tb:
            return False, Artifact(artifact_type="traceback", data=stdout_tb or stderr_tb)
        
        # If it succeeds, return None
        return True, None

class Router(ABC):
    @abstractmethod
    def next_action(self, artifacts: List[Artifact]) -> Action | None: # Might do better than None by having a special Action type to represent being done and successful
        raise NotImplementedError()

class Agent:
    history: List[EditDiff] = []
    llm: LLM
    filesystem: FileSystem
    router: Router

    def __init__(self, llm: LLM, validators: List[Validator], filesystem: FileSystem, router: Router, max_runs_per_validator: int = 1):
        self.llm = llm
        self.validators = validators
        self.filesystem = filesystem
        self.router = router
        self.max_runs_per_validator = max_runs_per_validator

    def _run_action(self, action: Action):
        edits = action.run(ActionParams(filesystem=self.filesystem, llm=self.llm))
        for edit in edits:
            # Should replace this with something inherent to EditDiff, this is slow. Also, do you want to use real diffs, or this, which is better for making suggestions?
            if edit.replacement == self.filesystem.read_range_in_file(RangeInFile(filepath=edit.filepath, range=edit.range)):
                continue
            print("Applying edit: ", edit)
            diff = self.filesystem.apply_file_edit(edit)
            self.history.append(diff)

    # Shouldn't it be able to run and check recursively? And keep track of the global number of loops?
    def run_and_check(self, action: Action) -> bool:
        """Run the agent, returning whether successful."""
        self._run_action(action)
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