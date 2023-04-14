from plugins import step
from ....libs.steps import StepParams
# Already here, you're seeing how bad it is that you're going to write
# matching Actions and Steps.
# In this case, you could solve it by having the FileSystem passed to
# the Step automatically record stuff, but this doesn't extend to everything
# else. I don't think it should be the responsibility of the Resource
# to record changes. That's Step or Runner.
# What you might do:
"""It's a lot like package.json and package-lock.json
Where package is like the __init__ parameters that tell the Step how to run
And package-lock is the description of how the step ran.
In some cases, the package is enough, like with FileEdit
But if there's some randomness, then no

Why can't you just return a function that does the reverse?
Because you want to serialize.
So instead, you just need a little more information.

Say you ran a language model so the result was complicated.
Or even just say you wrote a complicated function with loops and logic,
so reversing it is complicated.

The reverse method doesn't make sense, because you only find out after running
whether the step was reversible or not.
"""


class ThoughtStep:
    """A Step that thinks."""
    @step.hookimpl
    def run(params: StepParams):
        print("Thinking...")
