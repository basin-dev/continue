from typing import List
from ...models.main import AbstractModel
from abc import abstractmethod
from pydantic import BaseModel
from ...models.filesystem import FileSystem
from ...libs.llm import LLM

class StepOutput(BaseModel):
    observations: List["Observation"]
    history: History
    substeps: List["Action"]
    not_permitted: bool=False

class NotPermittedStepOutput(StepOutput):
    not_permitted: bool=True
    observations: List["Observation"] = []
    actions: List["Action"] = []

class Runner:
    """The Runner class is like middleware on all steps."""
    def __init__(self, agent, depth: int=0):
        self.depth = depth
        self.agent = agent

    def _ask_permission(self, step: "Step") -> bool:
        return input("Run step? (y/n)") == "y"
    
    def _sub_runner(self):
        return Runner(self.agent, depth=self.depth + 1)

    def run(self, step: "Step", require_permission: bool=False) -> "StepOutput":
        if require_permission:
            if not self._ask_permission(step):
                return NotPermittedStepOutput()

        step(StepParams(filesystem=self.agent.filesystem, llm=self.agent.llm, runner=self._sub_runner()))

class StepParams(BaseModel):
    filesystem: FileSystem
    llm: LLM
    runner: Runner

class Step(AbstractModel):
    @abstractmethod
    def run(self, params: StepParams) -> StepOutput:
        raise NotImplementedError
    
    def __call__(self, params: StepParams) -> StepOutput:
        return self.run(params)
    
class DoneStep(Step):
    def run(self, params: StepParams) -> StepOutput:
        return StepOutput(observations=[], history=None, substeps=[])