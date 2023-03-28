from typing import Callable, Dict, List, Tuple
from ..models.main import FileEdit, EditDiff, Traceback
from ..models.filesystem import FileSystem
from .main import Agent
from abc import ABC, abstractmethod
from pydantic import BaseModel
import subprocess
from .traceback_parsers import parse_python_traceback
from .actions.llm import LLM

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
    data: any

Action = Callable[[Agent, any], FileEdit]


# Enrichers!!!!
# This is what collects the debug context. You might start with a traceback, but then you run deterministic tools to enrich.
# Is an enricher different from an action? An enricher COULD just be an action, but it might be easier to read if separate.

Enricher = Callable[[Artifact], Artifact]

class Hook(BaseModel):
    artifact_type: str
    action: Action

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

        stdout_tb = parse_python_traceback(stdout)
        stderr_tb = parse_python_traceback(stderr)

        # If it fails, return the error
        if stdout_tb or stderr_tb:
            return False, Artifact(artifact_type="traceback", data=stdout_tb or stderr_tb)
        
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

class Agent:
    hook_registry: Dict[str, Action] = {}
    history: List[EditDiff] = []
    llm: LLM

    def __init__(self, llm: LLM, validators: List[Validator], hooks: List[Hook], max_runs_per_validator: int = 5):
        self.llm = llm
        self.validators = validators
        for hook in hooks:
            self.hook_registry[hook.artifact_type] = hook.action
        self.max_runs_per_validator = max_runs_per_validator

    def _run_action(self, fs: FileSystem, action: Action, data: any):
        edit = action(fs, data)
        diff = fs.apply_file_edit(edit)
        self.history.append(diff)

    # Shouldn't it be able to run and check recursively? And keep track of the global number of loops?
    def run_and_check(self, fs: FileSystem, action: Action, data: any) -> bool:
        """Run the agent, returning whether successful."""
        self._run_action(fs, action, data)
        success = self.fix_validators(fs)

        return success

    def fix_validators(self, fs: FileSystem) -> bool:
        """Attempt to run and fix all validators, returning whether successful."""
        """ Should probably also return WHY it was unsuccessful."""

        a_validator_failed = False
        for validator in self.validators:
            i = 0
            passed = False
            while i < self.max_runs_per_validator and not passed:
                passed, artifact = validator.run(fs)

                if passed:
                    passed = True
                else:
                    # Run the action that can fix this artifact
                    if artifact.artifact_type not in self.hook_registry:
                        raise Exception("No hook found for artifact type: " + artifact.artifact_type)
                    
                    # Apply the action and keep track of the diff
                    action = self.hook_registry[artifact.artifact_type]
                    self._run_action(fs, action, artifact.data)

                    # Then the validator is rerun --^
            
            if not passed:
                a_validator_failed = True
                break

        return a_validator_failed

# Maybe hooks better termed "routers" because validators are already doing most of the work