from plugins import policy
from ....libs.observation import Observation
from ....libs.steps import Step

class AlternatingPolicy:
    """A Policy that alternates between two steps."""

    def __init__(self, first: Step, second: Step):
        self.first = first
        self.second = second
        self.last_was_first = False

    @policy.hookimpl
    def next(self, observation: Observation | None=None) -> Step:
        if self.last_was_first:
            self.last_was_first = False
            return self.second
        else:
            self.last_was_first = True
            return self.first