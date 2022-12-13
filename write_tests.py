from llm import OpenAI

## UTILITIES ##
llm = OpenAI()

def whole_code_prompt(unit_test_framework: str, code_to_test: str) -> str:
    """Return the prompt for the unit test."""
    return f""""
    {code_to_test}
    "

    Write unit tests for the above code using {unit_test_framework}."""

def single_function_prompt(unit_test_framework: str, code_to_test: str) -> str:
    """Return the prompt for the unit test."""
    return f""""
    {code_to_test}
    "

    Write unit tests for the above function using {unit_test_framework}."""

def split_into_functions(code: str) -> list:
    """Split the code into a list of functions."""
    pass

def validate_tests(test_code: str) -> bool:
    """Check that the tests are valid."""
    pass

def write_to_file(test_code: str, file_name: str):
    """Write the test code to a file."""
    with open(file_name, "w") as f:
        f.write(test_code)


## PIPELINES ##

"""Here we write a series of pipelines to see which works best.
Different combinations of code splitting and context injection, different prompts, deterministic checkers/editors, etc."""
def naive_pipeline(unit_test_framework: str, code_to_test: str):
    """Generate unit tests in a single prompt."""
    prompt = whole_code_prompt(unit_test_framework, code_to_test)
    completion = llm.complete(prompt)
    
    return completion


def better_pipeine(unit_test_framework: str, code_to_test: str):
    """Split into functions and complete for each separately, no context."""
    functions = split_into_functions(code_to_test)

    tests = []

    for function in functions:
        prompt = single_function_prompt(unit_test_framework, code_to_test)
        completion = llm.complete(prompt)
        tests.append(completion)

    # May want to deduplicate any overhead code that it writes, or maybe it won't write any, we'll have to add separately.
    
    return "\n\n".join(tests)

def even_better_pipeine(unit_test_framework: str, code_to_test: str):
    """Split into functions and complete for each separately, adding context determined by analyzing dependencies in the code (which variables are used)."""
    pass
