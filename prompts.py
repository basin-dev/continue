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

import ast
from typing import Any, Callable, List, Tuple
from llm import LLM, OpenAI

# Helpers
def cls_method_to_str(cls_name: str, init: str, method: str) -> str:
    """Convert class and method info to formatted code"""
    return f"""class {cls_name}:
{init}
{method}"""


# Prompter classes - TODO: Consider baking retry policies into the prompter, or make this a wrapper class. Also deterministic short-circuiters, to avoid even having to use an LLM in like 80% of cases.
class Prompter:
    def __init__(self, **kwargs):
        self.llm = OpenAI()
        self.kwargs = kwargs

    def _compile_prompt(self, inp: Any) -> Tuple[str, str, str | None]:
        "Takes input and returns prompt, prefix, suffix"
        raise NotImplementedError

    def complete(self, inp: Any) -> str:
        prompt, prefix, suffix = self._compile_prompt(inp)
        resp = self.llm.complete(prompt + prefix, suffix=suffix, **self.kwargs)
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
        
        resps = self.llm.parallel_complete([prompt + prefix for prompt, prefix in zip(prompts, prefixes)], suffixes=suffixes, **self.kwargs)
        return [prefix + resp + (suffix or "") for prefix, resp, suffix in zip(prefixes, resps, suffixes)]

# Note that this can be used hierarchically : )
class MixedPrompter(Prompter):
    def __init__(self, prompters: List[Prompter], router: Callable[[Any], int], **kwargs):
        super().__init__(**kwargs)
        self.prompters = prompters
        self.router = router
    
    def _compile_prompt(self, inp: Any) -> Tuple[str, str, str | None]:
        prompter = self.prompters[self.router(inp)]
        return prompter._compile_prompt(inp)

    def complete(self, inp: Any) -> str:
        prompter = self.prompters[self.router(inp)]
        return prompter.complete(inp)

class SimplePrompter(Prompter):
    def __init__(self, prompt_fn: Callable[[Any], str], **kwargs):
        super().__init__(**kwargs)
        self.prompt_fn = prompt_fn

    def _compile_prompt(self, inp: Any) -> Tuple[str, str, str | None]:
        return self.prompt_fn(inp), "", None

class BasicCommentPrompter(SimplePrompter):
    def __init__(self, comment: str, **kwargs):
        super().__init__(lambda inp: f"""{inp}

# {comment}""", **kwargs)

class EditPrompter(Prompter):
    def __init__(self, prompt_fn: Callable[[Any], Tuple[str, str]], **kwargs):
        super().__init__(**kwargs)
        self.prompt_fn = prompt_fn
    
    def complete(self, inp: str, **kwargs) -> str:
        inp, instruction = self.prompt_fn(inp)
        return self.llm.edit(inp, instruction, **kwargs)

    def parallel_complete(self, inps: List[Any]) -> List[str]:
        prompts = []
        instructions = []
        for inp in inps:
            prompt, instruction = self.prompt_fn(inp)
            prompts.append(prompt)
            instructions.append(instruction)
        
        return self.llm.parallel_edit(prompts, instructions, **self.kwargs)

class InsertPrompter(Prompter):
    def __init__(self, prompt_fn: Callable[[Any], Tuple[str, str, str]], **kwargs):
        super().__init__(**kwargs)
        self.prompt_fn = prompt_fn
    
    def _compile_prompt(self, inp: Any) -> Tuple[str, str, str | None]:
        return self.prompt_fn(inp)

class FewShotPrompter(Prompter):
    def __init__(self, instruction: str, examples: List[Tuple[str, str]], formatter: Callable[[Tuple[str, str]], str], separator="\n\n--------\n\n", **kwargs):
        super().__init__(**kwargs)
        self.examples = examples
        self.formatter = formatter
        self.separator = separator
        self.instruction = instruction
    
    def _compile_prompt(self, inp: Any) -> Tuple[str, str, str | None]:
        return f"""{self.instruction}\n
{self.separator.join([self.formatter(example) for example in self.examples])}{self.separator}{self.formatter((inp, ""))}""", "", None

### Completion mode for unit test generation ###

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