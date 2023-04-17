from ... import step
from ....libs.steps import StepParams
from ....libs.observation import Observation
from ....libs.steps import Step, AddFile, FileEdit

class EditCodeStep(Step):
    """A Step that edits the code for a Continue step."""
    @step.hookimpl
    def run(params: StepParams) -> Observation:
        # TODO: implement code editing of steps and policies here