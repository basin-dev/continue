from abc import ABC, abstractmethod
from .llm import LLM
from .llm.prompters import FormatStringPrompter
from textwrap import dedent
from typing import Generator, List
from ..models.main import AbstractModel
from .steps import Step
from .observation import Observation

class Policy(AbstractModel):
    @abstractmethod
    def next(self, observation: Observation | None=None) -> Step: # Should probably be a list of observations, or perhaps just an observation subclass representing multiple observations
        raise NotImplementedError
    
class DemoPolicy(Policy):
    """
    This is the simplest policy I can think of.
    Will alternate between running and fixing code.
    """
    ran_code_last: bool = False

    def next(self) -> Step:
        if self.ran_code_last:
            self.ran_code_last = False
            return FixCodeStep()
        else:
            self.ran_code_last = True
            return RunCodeStep()

# Validator = Step # For now. Should be a subclass of Step

# class PolicyWithValidators(Policy):
#     """Default is to stop, unless the validator tells what to do next"""

#     def __init__(self, validators: List[Validator]):
#         self.validators = validators

#     def next(self) -> Step:
#         a_validator_failed = False
#         for validator in self.validators:
#             passed = self.fix_validator(validator)
#             if not passed:
#                 a_validator_failed = True
#                 break

#         return a_validator_failed

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