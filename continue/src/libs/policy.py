from typing import Generator, List, Tuple, Type

from .steps.ty import CreatePipelineStep
from .core import Agent, Step, Validator, Policy, History, UserInputStep
from .observation import Observation, TracebackObservation, UserInputObservation
from .steps.main import EditCodeStep, EditHighlightedCodeStep, SolveTracebackStep, RunCodeStep
from .steps.nate import WritePytestsStep


class DemoPolicy(Policy):
    """
    This is the simplest policy I can think of.
    Will alternate between running and fixing code.
    """
    ran_code_last: bool = False
    cmd: str

    def next(self, history: History) -> Step:
        observation = history.last_observation()
        if observation is not None and isinstance(observation, UserInputObservation):
            # This could be defined with ObservationTypePolicy. Ergonomics not right though.
            if "test" in observation.user_input.lower():
                return WritePytestsStep(instructions=observation.user_input)
            elif "dlt" in observation.user_input.lower():
                return CreatePipelineStep()
            return EditHighlightedCodeStep(user_input=observation.user_input)

        state = history.get_current()
        if state is None or not self.ran_code_last:
            self.ran_code_last = True
            return RunCodeStep(cmd=self.cmd)

        if observation is not None and isinstance(observation, TracebackObservation):
            self.ran_code_last = False
            return SolveTracebackStep(traceback=observation.traceback)
        else:
            return None
        # if self.ran_code_last:
        #     # A nicer way to define this with the Continue SDK: continue_sdk.on_observation_type(TracebackObservation, SolveTracebackStep, lambda obs: obs.traceback)
        #     # This is a way to iteratively define policies.
        #     """
        #     policy = BasePolicy().on_observation_type(TracebackObservation, SolveTracebackStep, lambda obs: obs.traceback)
        #         .on_observation_type(OtherObservation, SolveOtherStep, lambda obs: obs.other)
        #         .with_validators([Validator1, Validator2])
        #         ...etc...
        #     """
        #     # This is a really akward way to have to check the observation type.
        #     if observation is not None and isinstance(observation, TracebackObservation):
        #         self.ran_code_last = False
        #         return SolveTracebackStep(traceback=observation.traceback)
        #     else:
        #         return None
        # else:
        #     self.ran_code_last = True
        #     return RunCodeStep(cmd=self.cmd)


class ObservationTypePolicy(Policy):
    def __init__(self, base_policy: Policy, observation_type: Type[Observation], step_type: Type[Step]):
        self.observation_type = observation_type
        self.step_type = step_type
        self.base_policy = base_policy

    def next(self, history: History) -> Step:
        observation = history.last_observation()
        if observation is not None and isinstance(observation, self.observation_type):
            return self.step_type(observation)
        return self.base_policy.next(history)


class PolicyWrappedWithValidators(Policy):
    """Default is to stop, unless the validator tells what to do next"""
    index: int
    stage: int

    def __init__(self, base_policy: Policy, pairs: List[Tuple[Validator, Type[Step]]]):
        # Want to pass Type[Validator], or just the Validator? Question of where params are coming from.
        self.pairs = pairs
        self.index = len(pairs)
        self.validating = 0
        self.base_policy = base_policy

    def next(self, history: History) -> Step:
        if self.index == len(self.pairs):
            self.index = 0
            return self.base_policy.next(history)

        if self.stage == 0:
            # Running the validator at the current index for the first time
            validator, step = self.pairs[self.index]
            self.stage = 1
            return validator
        elif self.stage == 1:
            # Previously ran the validator at the current index, now receiving its ValidatorObservation
            observation = history.last_observation()
            if observation.passed:
                self.stage = 0
                self.index += 1
                if self.index == len(self.pairs):
                    self.index = 0
                    return self.base_policy.next(history)
                else:
                    return self.pairs[self.index][0]
            else:
                _, step_type = self.pairs[self.index]
                return step_type(observation)

# Problem is how to yield a Step while also getting its observation. You'd have to run the step within the policy in order to get its observation.
# This can be done from within a step, right?
# It was really ugly to write the above class, and ideally it would look like the below:

# @validator_from_generator
# def policy_with_validator(validators: List[Type[Validator]]):
#     a_validator_failed = False
#     for validator in validators:
#         passed = yield validator
#         passed = self.fix_validator(validator)
#         if not passed:
#             a_validator_failed = True
#             break

#     return a_validator_failed

# class ReActPolicy(Policy):
#     llm: LLM
#     prompt: str = dedent("""The available actions are:
#             {actions}

#             The next action I should take is:
#     """)

#     def __init__(self, llm: LLM):
#         self.llm = llm
#         self.prompter = FormatStringPrompter(self.prompt)
#         # This should be an EncoderDecoder Prompter subclass that parses for a single action name from a list of available actions

#     def next(self) -> Step:
#         pass

# # One question: there seem to be two ways to phrase validators: 1. is that they are like guardrails, considered more of a part of the prompt.
# # 2. They are just other actions that iteratively get to fixes.
# # I think certain things like type-checker errors can easily be a part of something like the Guardrails project, because they are mostly syntax-based.
# # But something like running the code shouldn't be
