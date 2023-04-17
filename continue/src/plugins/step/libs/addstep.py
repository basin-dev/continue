from ... import step
from ....libs.steps import StepParams
from ....libs.observation import Observation
from ....libs.steps import Step, AddFile, FileEdit

class AddStepStep(Step):
    """A Step that adds a new Continue step."""
    @step.hookimpl
    def run(params: StepParams) -> Observation:
        code = '''
        class MyStep(Step):
            async def run(self, params: StepParams):
                pass
        '''
        stepname = input()
        filename = stepname + ".py"
        params.run_step(AddFile(filename))
        params.run_step(FileEdit(filename, code))