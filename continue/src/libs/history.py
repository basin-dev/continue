from abc import abstractmethod
from typing import TypeVar, Generic, Tuple, List
from ..models.main import AbstractModel
from .steps import Step

T = TypeVar("T")

class DagNode(AbstractModel, Generic[T]):
    """A node in a DAG"""
    data: T
    dependencies: List["DagNode"]
    children: List["DagNode"]

class DAG(AbstractModel, Generic[T]):
    """A Directed Acyclic Graph"""
    start_nodes: List[DagNode[T]]
    end_nodes: List[DagNode[T]]

class History(DAG[Tuple[Step, History]]):
    """A history of actions taken"""
    current_node: DagNode[History]

class Action(AbstractModel):
    reversible: bool

class ReversibleAction(Action):
    reversible: bool = True

    @abstractmethod
    def reverse(self) -> Action:
        raise NotImplementedError
    
class ReversibleFileSystemAction(ReversibleAction):
    """TODO: See FileSystemEdit. That's basically what I want this to be."""