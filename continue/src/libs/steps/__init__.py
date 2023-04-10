from typing import List, Tuple
from ...models.main import AbstractModel
from abc import abstractmethod
from pydantic import BaseModel
from ...models.filesystem import FileSystem
from ..llm import LLM
from ..observation import Observation
from ..actions import Action

StepOutput = Tuple[Observation, Action]

class StepParams(AbstractModel):
    filesystem: FileSystem
    llm: LLM
    runner: "Runner" # No reason that filesystem and llm can't be class attributes of Step.
    # They're arbitrary things to be passing to each and every step.
    # So maybe the step should require them to be instantiated, but the default step can have them.

# If given a runner, don't return Action.
# If writing a step with CustomAction, then you need to return an Action, and don't get a runner
# Might be able to do something nice with a context manager, that can record all updates to filesystem or something, just let people write code more natually. idk
# As someone writing a step, I don't want to have to call everything from an existing Step in the library, or download someone else's plugin. That's annoying.
# And there are probably too many different actions to make a plugin for each one.
# For example, say I want to make a series of API calls.
# Bad case is I have to register all of them, create my own atomic actions. Especially bad if I'm running another defined step between each one.
# Basically, if I want something to be reversible, I'll make a custom sub-step. If not, just write the code. If it has to keep track of some state, maybe define a "Resource"
# But then the sub-step I want to define: If reversible, then I have to write a custom ReversibleAction? That's annoying because then I have
# to also worry about serializing stuff.
# In cases where something non-deterministic happens, like language model output, then you need to know that output of the Step before coming up with the reverse.
# But if deterministic, then you can know beforehand what the reverse will be. In which case, you can just reverse the action.

# What if there were a way to make it easy for developers to write the information they needed from forward pass to save for reverse?

# We might define reversibility inside of steps as follows:
"""class ReversibleStep("Step"):
    def reverse(self):
        if not self.has_been_run:
            raise ValueError("Step has not been run yet")
        raise NotImplementedError # Simply runs the code to do the reversal
    
    has_been_run: bool = False"""

# Reversible vs. no side-effect. no side-effect is trivially reversible

class Step(AbstractModel):
    @abstractmethod
    def run(self, params: StepParams) -> Observation:
        raise NotImplementedError
    
    def __call__(self, params: StepParams) -> Observation:
        return self.run(params)
    
class AtomicStep(Step):
    """A step that doesn't get a runner, but can create its own side-effects."""
    def run(self, params: StepParams) -> StepOutput:
        return self.run_with_side_effects(params.llm, params.filesystem)

    def run_with_side_effects(self, llm: LLM, filesystem: FileSystem) -> StepOutput:
        raise NotImplementedError
    
class DoneStep(Step):
    def run(self, params: StepParams) -> StepOutput:
        return None, None
    
class ValidatorObservation(Observation):
    passed: bool
    observation: Observation

class Validator(Step):
    def run(self, params: StepParams) -> ValidatorObservation:
        raise NotImplementedError
    



# T = TypeVar("T")

# class DagNode(AbstractModel, Generic[T]):
#     """A node in a DAG"""
#     data: T
#     dependencies: List["DagNode"]
#     children: List["DagNode"]

# class DAG(AbstractModel, Generic[T]):
#     """A Directed Acyclic Graph"""
#     start_nodes: List[DagNode[T]]
#     end_nodes: List[DagNode[T]]

# class History(DAG[Tuple[Step, History]]):
#     """A history of actions taken"""
#     current_node: DagNode[History]

class HistoryNode(AbstractModel):
    """A node in a DAG"""
    step: Step
    output: StepOutput | None

class History(AbstractModel):
    """A history of actions taken"""
    timeline: List[HistoryNode]
    current_index: int

class RunnerOutput(BaseModel):
    observations: List["Observation"]
    history: History

# A history is a composable DAG of actions (DAG of DAGs), OR a history is just a list, and the actions are the things that compose.

# I THINK best is that History is just a DAG, and actions are the things that compose. Parallelism then handled by runner. Nicely splits responsibilities. We'll see if it's possible.
# Might also be that History should be mixed with Runner.

# Runner doesn't necessarily need to return all this stuff.
# Just has to be responsible for updating the history.
# Might merge with the agent for this? Or probably not.
# Maybe we make a HistoryUpdate class? This could also be same thing sent to client.

class Runner:
    """The Runner class is like middleware on all steps."""
    history: History

    def __init__(self, agent):
        self.agent = agent
        self.history = History(timeline=[], current_index=0)

    def _ask_permission(self, step: "Step") -> bool:
        return input("Run step? (y/n)") == "y"

    def run(self, step: "Step", require_permission: bool=False) -> Observation: # TODO: require_permission happen elsewhere
        if isinstance(step, AtomicStep) or issubclass(step, AtomicStep):
            observation, action = step(StepParams(filesystem=self.agent.filesystem, llm=self.agent.llm, runner=self._sub_runner()))
        else:
            observation = step(StepParams(filesystem=self.agent.filesystem, llm=self.agent.llm, runner=self._sub_runner()))
            action = None
        self.history.timeline.append(HistoryNode(step=step, output=(observation, action)))
        return observation
