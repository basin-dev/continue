# Building a plugin

What are the simple building blocks that developers can use to define their own workflow automation?

- Simplest: hook and a prompt, that’s all
- ideally, they say, I want to do this when this happens
- at deepest level, should be able to create validator class as plugin, that specifies when to kickoff their thing

If you get to that, see the `continue/src/plugins/step/libs` folder for examples.

Essentially just copy that and write whatever code you want inside the function.

## Tutorial: Building your first Step plugin

### Hello World Step

Begin by adding the file where you will write your plugin: `continue/src/plugins/step/libs/<my_plugin_name>.py`.

First, import the plugin registration manager and necessary types:

```python
from plugins import step
from ....libs.steps import StepParams
```

The `step` file you've imported contains the `hookimpl` object that will let you specify where you are defining your implementation. Let's do this, and write an action that says "Hello World!":

```python
@step.hookimpl
def run(params: StepParams):
    print("Hello World!")
```

To explain what's going on here, you should first understand the concept of a [`Step`](../concepts/steps.md). Steps are anything that you or the autopilot might do, and they are called with their `run` method. By defining this method, you are writing what should happen when the step is called. In this case, we just printing "Hello World!".

### Composability and Reversibility

An important feature of Steps is their composability. In fact, for most Steps that you write, you'll use our built-in library of foundational Steps to achieve many of the things you want to do. For example, let's say we want to write a Step that creates 5 files named `file_n.txt` and writes the corresponding number inside.

We can use the built-in `AddFile` and `FileEdit` Steps as follows:

```python
from plugins import step
from ....libs.steps import StepParams
from ??? import AddFile, FileEdit

@step.hookimpl
def run(params: StepParams) -> Observation:
    for i in range(5):
        filename = "file_" + str(i) + ".py"
        params.run_step(AddFile(filename))
        params.run_step(FileEdit(Range.from_shorthand(0, 0, 0, 0), filename, str(i)))
```

The benefit of calling sub-Steps with the `Runner` is that we automatically keep track of changes for you so that the UI can display them and so that your Step automatically becomes reversible.

Note that no `Observation` is returned here...

### Writing Steps with Observations

TODO

### Writing Steps with Side-Effects

When you can't find a Step to do what you want, it's time to create your own side-effects. TODO

```python
class AtomicStep(Step):
    """A step that doesn't get a runner, but can create its own side-effects."""
    def run(self, params: StepParams) -> StepOutput:
        return self.run_with_side_effects(params.llm, params.filesystem)

    def run_with_side_effects(self, llm: LLM, filesystem: FileSystem) -> StepOutput:
        raise NotImplementedError
```

## Tutorial: Building a Policy plugin

### Simple Alternating Policy

A Policy simply tells the Autopilot which Step it should take next. Having already built a Step plugin, this will be slightly easier. This time, make the file `continue/src/plugins/policy/libs/<policy_name>.py` like this:

```python
from plugins import policy
from ....libs.observation import Observation
from ....libs.steps import Step

class AlternatingPolicy:
    """A Policy that alternates between two steps."""

    def __init__(self, first: Step, second: Step):
        self.first = first
        self.second = second
        self.last_was_first = False

    @policy.hookimpl
    def next(self, observation: Observation | None=None) -> Step:
        if self.last_was_first:
            self.last_was_first = False
            return self.second
        else:
            self.last_was_first = True
            return self.first
```

As before, we use the `hookimpl` decorator to locate our implementation, but this time it is inside of a class. A `Step` is actually also a class, but for convenience you can decide to only define the functions if you do not require the ability to store state. In this case, we do want state because we want to know which Step was taken last.

When the policy is created it will be given 2 parameters, which are the `first` and `second` steps to run. The `next` function takes in the `Observation` (output of the previously run Step) and returns the Step to take next.

### Combining Policies

Sometimes, you'll want to borrow the logic from more than one Policy to make a better Policy. For example, say you a baseline Policy you'd like to run, but if any of the Steps taken have an observation of the `SomeoneSaidHello` type, then you wish to respond with a greeting. You might write something like this:

```python
class PolicyWithGreeting(Policy):
    def __init__(self, base_policy: Policy):
        self.base_policy = base_policy

    def next(self, observation: Observation | None=None) -> Step:
        if isinstance(observation, SomeoneSaidHello):
                return RespondWithGreeting(observation.someone.name)
        return self.base_policy.next(observation)
```

There are built-in ways to do certain things like this. In `continue/src/libs/policy.py`, there are the `ObservationTypePolicy` (which does something similar to this, except for some arbitrary observation type and step type) and the `PolicyWrappedWithValidators`, which runs a set of checks between every step.

# Questions

- [ ] What are step params?
- [ ] How do I know when something should be one or two steps?
- [ ] why is the decorator a @step.hookimpl? does the function name need to be named run with the step params as the argument?
- [ ] Where do I call the foundation model?
- [ ] Where do I specify the prompt?
- [ ] Where do I set the system message?
- [ ] How does the context window slide and the max response length adjust?
- [ ] I have to create a file for every step?
- [ ] what does a step with side-effects not get a runner? how do you define a side-effect?
- [ ] where is the natural language input at any time represented?
