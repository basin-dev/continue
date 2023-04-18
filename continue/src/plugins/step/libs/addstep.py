from ... import step
from ....libs.steps import StepParams
from ....libs.observation import Observation
from ....libs.steps import Step, AddFile, FileEdit

class AddStepStep(Step):
    """A Step that adds a new Continue step."""
    @step.hookimpl
    async def run(params: StepParams) -> Observation:
        filename = "generic_step.py"
        code = '''
        class MyStep(Step):
            async def run(self, params: StepParams):
                pass
        '''
        await params.ide.applyFileSystemEdit(AddFile(filepath=filename, content=code))