from ... import step
from ....libs.steps import StepParams
from ....libs.observation import Observation
from ....libs.steps import Step
from ....libs.steps import EditCodeStep

class EditPolicyStep(Step):
    """A Step that edits the code for a Continue policy."""
    @step.hookimpl
    def run(params: StepParams) -> Observation:
        # How does this step know what policy file to edit?
        # if it has not been edited yet:
            # rename file if it is still generic_policy.py
            # replace boilerplate code with an initial implementation
        # else:
            # edit existing code based on descriptions
        params.run(EditCodeStep())