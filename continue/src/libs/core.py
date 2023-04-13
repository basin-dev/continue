from abc import ABC
import inspect
import asyncio
from typing import Callable, Generator, List, Tuple, Union
from ..models.filesystem import FileSystem, RangeInFile, RealFileSystem
from pydantic import BaseModel, parse_file_as, validator
from .llm import LLM
from .observation import Observation


class Policy(BaseModel):
    """A rule that determines which step to take next"""

    def next(self, observation: Observation | None = None) -> "Step":
        raise NotImplementedError


class HistoryNode(BaseModel):
    """A point in history, a list of which make up History"""
    step: "Step"
    output: Union["StepOutput", None]


class History(BaseModel):
    """A history of steps taken and their results"""
    timeline: List[HistoryNode]
    current_index: int


class StepParams:
    """The SDK provided as parameters to a step"""
    filesystem: FileSystem
    llm: LLM
    __agent: "Agent"

    def __init__(self, agent: "Agent"):
        self.filesystem = agent.filesystem
        self.llm = agent.llm
        self.__agent = agent

    def run_step(self, step: "Step") -> Observation:
        return self.__agent._run_singular_step(step)


class Agent(BaseModel):
    llm: LLM
    filesystem: FileSystem = RealFileSystem()
    active: bool = False
    policy: Policy
    history: History = History(timeline=[], current_index=0)
    _on_step_callbacks: List[Callable[["Step"], None]] = []

    def on_step(self, callback: Callable[["Step"], None]):
        self._on_step_callbacks.append(callback)

    def __ask_permission(self, step: "Step") -> bool:
        return input("Run step? (y/n)") == "y"

    def __get_step_params(self):
        return StepParams(agent=self)

    def _run_singular_step(self, step: "Step") -> Observation:
        step_params = self.__get_step_params()

        # Get observation and action from running either Step or AtomicStep
        if isinstance(step, AtomicStep) or issubclass(step.__class__, AtomicStep):
            observation, action = step(step_params)
        else:
            output = step(step_params)
            if issubclass(step.__class__, AtomicStep):
                observation, action = output
            else:
                observation = output
                action = None

        # Update history
        self.history.timeline.append(
            HistoryNode(step=step, output=(observation, action)))

        # Call all subscribed callbacks
        for callback in self._on_step_callbacks:
            callback(step)

        return observation

    def run_from_step(self, step: "Step"):
        if self.active:
            raise RuntimeError("Agent is already running")
        self.active = True

        next_step = step
        while not (next_step is None or isinstance(next_step, DoneStep)):
            observation = self._run_singular_step(next_step)
            next_step = self.policy.next(observation)

    def run_from_observation(self, observation: Observation):
        next_step = self.policy.next(observation)
        self.run_from_step(next_step)

    def run_policy(self):
        first_step = self.policy.next(None)
        self.run_from_step(first_step)


class Step(BaseModel):
    name: str = None
    _manual_description: str | None = None

    def describe(self) -> str:
        if self._manual_description is not None:
            return self._manual_description
        return "Running step: " + self.name

    def _set_description(self, description: str):
        self._manual_description = description

    def dict(self, *args, **kwargs):
        d = super().dict(*args, **kwargs)
        if self._manual_description is not None:
            d["description"] = self._manual_description
        else:
            d["description"] = self.describe()
        return d

    @validator("name", pre=True, always=True)
    def name_is_class_name(cls, name):
        print("Name is ", name)
        if name is None:
            return cls.__name__
        return name

    def run(self, params: StepParams) -> Observation:
        raise NotImplementedError

    def __call__(self, params: StepParams) -> Observation:
        return self.run(params)


class AtomicStep(Step):
    """A step that doesn't get a runner (TODO), but can create its own side-effects."""

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


class Action(BaseModel):
    reversible: bool = False

    def next_action(self) -> Generator["Action", None, None]:
        yield self

    def describe(self) -> str:  # This will be used by LLM to generate summaries. This might be a good reason for creation of many Edit classes
        return self.__repr__()


StepOutput = Tuple[Observation | None, Action | None]

HistoryNode.update_forward_refs()
