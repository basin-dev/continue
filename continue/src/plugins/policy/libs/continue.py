from plugins import policy
from ....libs.observation import Observation
from ....libs.steps import Step
from ....libs.core import History


class ContinuePolicy:
    """A policy that helps you write Continue plugins."""

    def __init__(self):
        self.selection = "user selection"
        self.initialize = True

    @policy.hookimpl
    def next(self, history: History) -> Step:
        if self.initialize:
            # TODO: add step
            # TODO: add policy
            self.initialize = False
        if self.selection == "add_step":
            # TODO: add step
            self.selection = "edit_step"
        elif self.selection == "edit_step":
            # rename if step has a generic name
            # replace if still boilerplate code
            # edit if not boilerplate code
            self.selection = None
        elif self.selection == "edit_policy"
            # rename if policy has a generic name
            # replace if still boilerplate code
            # edit if not boilerplate code
        else:
            # TODO: do something