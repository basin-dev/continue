from plugins import policy
from ....libs.observation import Observation
from ....libs.steps import Step
from ....libs.core import History
from ....libs.steps import AddPolicyStep, AddStepStep, EditStepStep, EditPolicyStep, NaturalLanguageUserInputStep, DoneStep


class ContinuePolicy(Policy):
    """A policy that helps you write Continue plugins."""

    def __init__(self):
        self.selection = None
        self.initialize = True

    @policy.hookimpl
    def next(self, history: History) -> Step:
        
        if self.initialize:
            AddPolicyStep()
            AddStepStep()
            self.initialize = False
            self.selection = "edit_step"

        if self.selection == "add_step":
            AddStepStep()
            EditStepStep()
            self.selection = None
        elif self.selection == "edit_step":
            EditStepStep()
            self.selection = None
        elif self.selection == "edit_policy":
            EditPolicyStep()
            self.selection = None
        elif self.selection == "done":
            DoneStep()
        else:
            NaturalLanguageUserInputStep("Do you want to add_step, edit_step, or edit_policy? If not, type done.")
        