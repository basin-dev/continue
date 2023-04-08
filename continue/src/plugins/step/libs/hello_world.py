from plugins import step
from ....libs.steps import StepParams

@step.hookimpl
def run(params: StepParams):
    print("Hello World!")