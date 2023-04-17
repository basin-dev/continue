from ... import step
from ....libs.steps import StepParams
from ....libs.observation import Observation
from ....libs.steps import Step, AddFile, FileEdit

class AddPolicyStep(Step):
    """A Step that adds a new Continue policy"""
    @step.hookimpl
    def run(params: StepParams) -> Observation:
        