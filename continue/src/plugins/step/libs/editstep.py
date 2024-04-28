from ... import step
from ....libs.steps import StepParams
from ....libs.observation import Observation
from ....libs.steps import Step
from ....libs.steps import EditCodeStep

class EditStepStep(Step):
    """A Step that edits the code for a Continue step."""
    @step.hookimpl
    def run(params: StepParams) -> Observation:
        # How does this step know what step file to edit?
        # if it has not been edited yet:
            # rename file if it is still generic_step.py
            # replace boilerplate code with an initial implementation
        # else:
            # edit existing code based on descriptions
        params.run(EditCodeStep())