from plugins import policy
from ....libs.observation import Observation
from ....libs.steps import Step
from ....libs.core import History


class ContinuePolicy:
    """A policy that helps you write Continue plugins."""

    def __init__(self):
        self.another_step = True

    @policy.hookimpl
    def next(self, history: History) -> Step:
        while self.another_step:
            yield AddStep
            yield EditCodeStep
        yield AddPolicyStep
        yield EditCodeStep