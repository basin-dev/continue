from abc import ABC
from typing import Generator, List, Tuple, Union
from ..models.filesystem import FileSystem, RangeInFile, RealFileSystem
from pydantic import BaseModel, parse_file_as
from .llm import LLM
from .observation import Observation

class Policy(BaseModel):
    def next(self, observation: Observation | None=None) -> "Step": # Should probably be a list of observations, or perhaps just an observation subclass representing multiple observations
        raise NotImplementedError

class Agent(BaseModel):
    llm: LLM
    filesystem: FileSystem
    active: bool = False
    policy: Policy

    def run_from_step(self, step: "Step", require_permission: bool=False):
        if self.active:
            raise RuntimeError("Agent is already running")
        self.active = True

        next_step = step
        runner = Runner(agent=self)
        # Make it a generator!
        while not (next_step is None or isinstance(next_step, DoneStep)):
            observation = runner.run(next_step) # Should the runner be the thing keeping track of history from outputs?
            next_step = self.policy.next(observation)

    def run_from_observation(self, observation: Observation):
        next_step = self.policy.next(observation)
        self.run_from_step(next_step)

class StepParams(BaseModel):
    filesystem: FileSystem
    llm: LLM
    runner: "Runner"

class Step(BaseModel):
    def run(self, params: StepParams) -> Observation:
        raise NotImplementedError
    
    def __call__(self, params: StepParams) -> Observation:
        return self.run(params)
    
class AtomicStep(Step):
    """A step that doesn't get a runner, but can create its own side-effects."""
    def run(self, params: StepParams) -> "StepOutput":
        return self.run_with_side_effects(params.llm, params.filesystem)

    def run_with_side_effects(self, llm: LLM, filesystem: FileSystem) -> "StepOutput":
        raise NotImplementedError
    
    # def with_validators(self, pairs: List[Tuple[Validator, Type[Step]]]) -> "PolicyWrappedWithValidators":
    #     """Create a policy that is the same except follows each step by running the validators and fixing with the matched step types."""
    #     return PolicyWrappedWithValidators(self, pairs)
    
    # def with_observation_type(self, observation_type: Type[Observation], step_type: Type[Step]) -> "ObservationTypePolicy":
    #     """Create a policy that is the same except always responds to this observation type with the specified step type."""
    #     return ObservationTypePolicy(self, observation_type, step_type)
    
class DoneStep(AtomicStep):
    def run(self, params: StepParams) -> "StepOutput":
        return None, None
    
class ValidatorObservation(Observation):
    passed: bool
    observation: Observation

class Validator(Step):
    def run(self, params: StepParams) -> ValidatorObservation:
        raise NotImplementedError

class HistoryNode(BaseModel):
    """A node in a DAG"""
    step: Step
    output: Union["StepOutput", None]

class History(BaseModel):
    """A history of actions taken"""
    timeline: List[HistoryNode]
    current_index: int

class RunnerOutput(BaseModel):
    observations: List["Observation"]
    history: History

class Runner(BaseModel):
    """The Runner class is like middleware on all steps."""
    history: History = History(timeline=[], current_index=0)
    agent: Agent

    def _ask_permission(self, step: "Step") -> bool:
        return input("Run step? (y/n)") == "y"

    def run(self, step: "Step", require_permission: bool=False) -> Observation: # TODO: require_permission happen elsewhere
        if isinstance(step, AtomicStep) or issubclass(step.__class__, AtomicStep):
            observation, action = step(StepParams(filesystem=self.agent.filesystem, llm=self.agent.llm, runner=self))
        else:
            output = step(StepParams(filesystem=self.agent.filesystem, llm=self.agent.llm, runner=self))
            if issubclass(step.__class__, AtomicStep):
                observation, action = output
            else:
                observation = output
                action = None
        self.history.timeline.append(HistoryNode(step=step, output=(observation, action)))
        return observation
    

class Action(BaseModel):
    reversible: bool = False

    def next_action(self) -> Generator["Action", None, None]:
        yield self

    def describe(self) -> str: # This will be used by LLM to generate summaries. This might be a good reason for creation of many Edit classes
        return self.__repr__()

StepOutput = Tuple[Observation | None, Action | None]

StepParams.update_forward_refs()
HistoryNode.update_forward_refs()