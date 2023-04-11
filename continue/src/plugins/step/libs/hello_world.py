from ....plugins import step
from ....libs.steps import StepParams

class HelloWorldStep:
    """A Step that prints "Hello World!"."""
    @step.hookimpl
    def run(params: StepParams):
        print("Hello World!")