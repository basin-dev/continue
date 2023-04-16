import time
from typing import Callable, Coroutine, Generator, List, Tuple, Union
from ..models.filesystem import FileSystem, RangeInFile, RealFileSystem
from pydantic import BaseModel, parse_file_as, validator
from .llm import LLM
from .observation import Observation, UserInputObservation
from ..server.ide_protocol import AbstractIdeProtocolServer


class ContinueBaseModel(BaseModel):
    class Config:
        underscore_attrs_are_private = True


class HistoryNode(ContinueBaseModel):
    """A point in history, a list of which make up History"""
    step: "Step"
    observation: Observation | None


class History(ContinueBaseModel):
    """A history of steps taken and their results"""
    timeline: List[HistoryNode]
    current_index: int

    def add_node(self, node: HistoryNode):
        self.timeline.append(node)
        self.current_index += 1

    def get_current(self) -> HistoryNode | None:
        if self.current_index < 0:
            return None
        return self.timeline[self.current_index]

    def last_observation(self) -> Observation | None:
        state = self.get_current()
        if state is None:
            return None
        return state.observation

    @classmethod
    def from_empty(cls):
        return cls(timeline=[], current_index=-1)


class FullState(ContinueBaseModel):
    """A full state of the program, including the history"""
    history: History
    active: bool


class Policy(ContinueBaseModel):
    """A rule that determines which step to take next"""

    # Note that history is mutable, kinda sus
    def next(self, history: History = History.from_empty()) -> "Step":
        raise NotImplementedError


class StepParams:
    """The SDK provided as parameters to a step"""
    filesystem: FileSystem
    llm: LLM
    ide: AbstractIdeProtocolServer
    __agent: "Agent"

    def __init__(self, agent: "Agent"):
        self.filesystem = agent.filesystem
        self.llm = agent.llm
        self.ide = agent.ide
        self.__agent = agent

    async def run_step(self, step: "Step") -> Coroutine[Observation, None, None]:
        return await self.__agent._run_singular_step(step)

    def get_history(self) -> History:
        return self.__agent.history


class Agent(ContinueBaseModel):
    llm: LLM
    policy: Policy
    ide: AbstractIdeProtocolServer
    filesystem: FileSystem = RealFileSystem()
    history: History = History.from_empty()
    _on_step_callbacks: List[Callable[["Step"], None]] = []

    _active: bool = False
    _should_halt: bool = False

    class Config:
        arbitrary_types_allowed = True

    def get_full_state(self) -> FullState:
        return FullState(history=self.history, active=self._active)

    def on_step(self, callback: Callable[["Step"], None]):
        self._on_step_callbacks.append(callback)

    def __ask_permission(self, step: "Step") -> bool:
        return input("Run step? (y/n)") == "y"

    def __get_step_params(self):
        return StepParams(agent=self)

    async def _run_singular_step(self, step: "Step") -> Coroutine[Observation, None, None]:
        # Run step
        observation = await step(self.__get_step_params())

        # Update its description
        step._set_description(await step.describe(self.llm))

        # Update history
        self.history.add_node(HistoryNode(step=step, observation=observation))

        # Call all subscribed callbacks
        for callback in self._on_step_callbacks:
            callback(step)

        return observation

    async def run_from_step(self, step: "Step"):
        if self._active:
            raise RuntimeError("Agent is already running")
        self._active = True

        next_step = step
        while not (next_step is None or isinstance(next_step, DoneStep) or self._should_halt):
            observation = await self._run_singular_step(next_step)
            next_step = self.policy.next(self.history)

        self._active = False

        # Doing this so active can make it to the frontend after steps are done. But want better state syncing tools
        for callback in self._on_step_callbacks:
            callback(None)

    async def run_from_observation(self, observation: Observation):
        next_step = self.policy.next(self.history)
        await self.run_from_step(next_step)

    async def run_policy(self):
        first_step = self.policy.next(self.history)
        await self.run_from_step(first_step)

    async def accept_user_input(self, user_input: str):
        if self._active:
            self._should_halt = True
            while self._active:
                time.sleep(0.1)
        self._should_halt = False

        # Just run the step that takes user input, and
        # then up to the policy to decide how to deal with it.
        await self.run_from_step(UserInputStep(user_input=user_input))


class Step(ContinueBaseModel):
    name: str = None
    hide: bool = False
    _description: str | None = None

    async def describe(self, llm: LLM) -> str:
        if self._description is not None:
            return self._description
        return "Running step: " + self.name

    def _set_description(self, description: str):
        self._description = description

    def dict(self, *args, **kwargs):
        d = super().dict(*args, **kwargs)
        if self._description is not None:
            d["description"] = self._description
        else:
            d["description"] = self.name
        return d

    @validator("name", pre=True, always=True)
    def name_is_class_name(cls, name):
        if name is None:
            return cls.__name__
        return name

    async def run(self, params: StepParams) -> Coroutine[Observation, None, None]:
        raise NotImplementedError

    async def __call__(self, params: StepParams) -> Coroutine[Observation, None, None]:
        return await self.run(params)


class ReversibleStep(Step):
    def reverse(self, params: StepParams):
        raise NotImplementedError


class UserInputStep(Step):
    user_input: str
    name: str = "User Input"
    hide: bool = True

    async def describe(self, llm: LLM) -> str:
        return self.user_input

    async def run(self, params: StepParams) -> Coroutine[UserInputObservation, None, None]:
        return UserInputObservation(user_input=self.user_input)


class DoneStep(ReversibleStep):
    async def run(self, params: StepParams) -> Coroutine[Observation, None, None]:
        return None


class ValidatorObservation(Observation):
    passed: bool
    observation: Observation


class Validator(Step):
    def run(self, params: StepParams) -> ValidatorObservation:
        raise NotImplementedError


HistoryNode.update_forward_refs()
