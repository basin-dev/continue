from textwrap import dedent
from typing import Coroutine
from ...models.main import Range
from ...models.filesystem import RangeInFile
from ...models.filesystem_edit import AddDirectory, AddFile
from ..observation import Observation
from ..core import History, Step, StepParams, Policy
from .main import EditCodeStep
import os

class AskAPIStep(Step):
    def run(params: StepParams) -> Observation:
        # should pause and wait until user provides an answer
        return "What API do I want to load data from? The destination of the dlt pipeline will be DuckDB"

class InitPipelineStep(Step):
    def run(params: StepParams) -> Observation:
        requested_api = # how can I pass in the API name in from the user?
        source_name = params.run_step(NamePipelineStep(requested_api))
        params.run_step(CLICommand(f'dlt init {source_name} duckdb'))
        params.run_step(GPT4Step('...')) # but I want to append it to the what API to use?

class AddAPIKeyStep(Step):
    def run(params: StepParams) -> Observation:
        # should pause until user takes manual action to add API key to the secrets.toml file
        return "Please add the API key to the `secrets.toml` file. I will continue working on the pipeline once it is there"

class CheckAPIReturnsStep(Step):
    def run(params: StepParams) -> Observation:
        # runs once there is an api key in `secrets.toml`
        output = params.run_step(CLICommand('python3 {source_name}.py'))
        params.run_step(CheckAPISuccessStep(output))
        
class CreatePipelinePolicy(Policy):
    _current_state: str = "init"

    def next(self, history: History=History.from_empty()) -> "Step":
        if self._current_state == "init":
            # something
            self._current_state = "second"
            return InitPipelineStep()
        elif self._current_state == "second":
            # do second thing
            self._current_state = "done"
            return 
        elif self._current_state == "done":
            # done
            return None
        else:
            # done
            return None
    