# This file contains prompts to use for generating pytests
# Other ideas:
# Purposefully clean up anything that was created during the test (this can be done deterministically at least for files)
# Edit mode on fixtures or however you make a mock class in pytest
# Need to do something about digests - for now, they just won't pass
# Sometimes the completion is just cut short. Should be able to identify this
# Sometimes errors because of undefined variables being hallucinated. You can parse to detect whether they are undefined, then perhaps replace with something that does exist. Probably not useful though.
# Messed up a few times by using file_storage fixture as a variable instead of calling it like the function it should...or something
# Can we deduplicate fixtures if there a multiple which do the same thing? Deduplicating by meaning instead of just string matching is important. Also intelligently combining them. Don't want to change order of tests though probably.
# Check for coverage, generate more tests intelligently if not 100%
# Add stop token






# Small tests:
# fn_1: 4/10
# fn_2: 5/10
# fn_3: 5/10
# general_1: 8/10
# fn_edit_check_return:

"""
Tests on full utils.py:

fn_1
Total tests: 24
Passing Tests: 9
Failed to parse: 2
Failed to run: 0
Did not pass: 13

fn_2
Total tests: 24
Passing Tests: 11
Failed to parse: 1
Failed to run: 0
Did not pass: 12

fn_3
Total tests: 24
Passing Tests: 12
Failed to parse: 1
Failed to run: 4
Did not pass: 7

general_1
Total tests: 24
Passing Tests: 14
Failed to parse: 0
Failed to run: 0
Did not pass: 10

fn_edit_check_return
Total tests: 24
Passing Tests: 5
Failed to parse: 2
Failed to run: 0
Did not pass: 17



"""

import ast
from typing import Any, Callable, List, Tuple
from llm import LLM, OpenAI

# Helpers
def cls_method_to_str(cls_name: str, init: str, method: str) -> str:
    """Convert class and method info to formatted code"""
    return f"""class {cls_name}:
{init}
{method}"""


# Prompter classes
class Prompter:
    def __init__(self):
        self.llm = OpenAI()

    def _compile_prompt(self, inp: Any) -> Tuple[str, str, str | None]:
        "Takes input and returns prompt, prefix, suffix"
        raise NotImplementedError

    def complete(self, inp: Any) -> str:
        prompt, prefix, suffix = self._compile_prompt(inp)
        resp = self.llm.complete(prompt + prefix, suffix=suffix)
        return prefix + resp + (suffix or "")

    def parallel_complete(self, inps: List[Any]) -> List[str]:
        prompts = []
        prefixes = []
        suffixes = []
        for inp in inps:
            prompt, prefix, suffix = self._compile_prompt(inp)
            prompts.append(prompt)
            prefixes.append(prefix)
            suffixes.append(suffix)
        
        resps = self.llm.parallel_complete([prompt + prefix for prompt, prefix in zip(prompts, prefixes)], suffixes=suffixes)
        return [prefix + resp + (suffix or "") for prefix, resp, suffix in zip(prefixes, resps, suffixes)]

# Note that this can be used hierarchically : )
class MixedPrompter(Prompter):
    def __init__(self, prompters: List[Prompter], router: Callable[[Any], int]):
        super().__init__()
        self.prompters = prompters
        self.router = router
    
    def _compile_prompt(self, inp: Any) -> Tuple[str, str, str | None]:
        prompter = self.prompters[self.router(inp)]
        return prompter._compile_prompt(inp)

    def complete(self, inp: Any) -> str:
        prompter = self.prompters[self.router(inp)]
        return prompter.complete(inp)

class SimplePrompter(Prompter):
    def __init__(self, prompt_fn: Callable[[Any], str]):
        super().__init__()
        self.prompt_fn = prompt_fn

    def _compile_prompt(self, inp: Any) -> Tuple[str, str, str | None]:
        return self.prompt_fn(inp), "", None

class BasicCommentPrompter(SimplePrompter):
    def __init__(self, comment: str):
        super().__init__(lambda inp: f"""{inp}

# {comment}""")

class InsertPrompter(Prompter):
    def __init__(self, prompt_fn: Callable[[Any], Tuple[str, str, str]]):
        super().__init__()
        self.prompt_fn = prompt_fn
    
    def _compile_prompt(self, inp: Any) -> Tuple[str, str, str | None]:
        return self.prompt_fn(inp)


# Edit mode
def _fn_insert_compiler(fn_code: str) -> str:
    # This is only if the function has a return
    fn = ast.parse(fn_code).body[0]
    args = ", ".join([arg.arg for arg in fn.args.args])
    test_args = args + ", expected"
    prompt = f"""{fn_code}

# Write multiple Python unit tests using the pytest library for the above function, using parameterizations and doing a proper partitioning of the input space:

"""
    prefix = f"""@pytest.mark.parametrize("{test_args}", [
    """
    suffix = f"""
])
def test_{fn.name}({test_args}):
    assert {fn.name}({args}) == expected
"""
    return prompt, prefix, suffix

fnInsertPrompter = InsertPrompter(_fn_insert_compiler)


# Completion mode
def general_1(code: str) -> str:
    return f"""{code}

# Write tests for the above code using pytest. Consider doing any of the following as needed: writing mocks, creating fixtures, using parameterization, setting up, and tearing down. All tests should pass:"""

def fn_1(fn_code: str) -> str:
    return f"""{fn_code}

# Write multiple Python unit tests using the pytest library for the above function, using parameterizations and doing a proper partitioning of the input space:"""

def fn_2(fn_code: str) -> str:
    return f"""{fn_code}

# Write multiple Python unit tests using the pytest library for the above function, ensuring 100% coverage of the lines:"""

def fn_3(fn_code: str) -> str:
    fn_name = ast.parse(fn_code).body[0].name
    return f"""{fn_code}

# Write tests for the {fn_name} function using pytest. Consider doing any of the following as needed: writing mocks, creating fixtures, partitioning the input space, setting up, and tearing down:"""

def cls_1(cls_name: str, init: str, method: str) -> str:
    prompt = f"""{cls_method_to_str(cls_name, init, method)}

# Write multiple Python unit tests using the pytest library for the above class and its {method.split("def ")[1].split("(")[0]} method, using fixtures and parameterizations and doing a proper partitioning of the input space:"""
    return prompt

# Mock a class
def cls_mock(cls_name: str, init: str, method: str) -> str:
    return f"""{cls_method_to_str(cls_name, init, method)}

# Create a mocked version of the above class in order to use with pytest:"""

# Use the mocked class to write tests
def cls_with_mock(cls_name: str, init: str, method: str, mock: str) -> str:
    return f"""{cls_method_to_str(cls_name, init, method)}
    
{mock}

# Use mock version of the {cls_name} class to write pytest tests for the {method} method:"""