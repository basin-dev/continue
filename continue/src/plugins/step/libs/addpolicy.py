from ... import step
from ....libs.steps import StepParams
from ....libs.observation import Observation
from ....libs.steps import Step, AddFile, FileEdit

class AddPolicyStep(Step):
    """A Step that adds a new Continue policy."""
    @step.hookimpl
    async def run(params: StepParams) -> Observation:
        filename = "generic_policy.py"
        code = '''
        class MyPolicy(Policy):
            
            def __init__(self):
                pass
            
            @policy.hookimpl
            def next(self, history: History) -> Step:
                pass
        '''
        await params.ide.applyFileSystemEdit(AddFile(filepath=filename, content=code))