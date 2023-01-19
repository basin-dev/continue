import os
from llm import OpenAI, LLM, HuggingFace
from parse import compile_prompt as c_p

## UTILITIES ##
tuned_model = "davinci:ft-personal:pytest-davinci-1-2023-01-04-23-41-34"

# Previously fine-tuned models
# davinci:ft-personal-2022-12-15-19-12-04
# curie:ft-personal-2023-01-01-18-44-14
# Accidentally trained on only the handwritten code I wanted to test: curie:ft-personal-2023-01-02-18-42-04
# Latest Curie (after getting 243 examples of pytest): curie:ft-personal-2023-01-03-05-09-08
# $30 Davinci: davinci:ft-personal:pytest-davinci-1-2023-01-04-23-41-34

def whole_code_prompt(unit_test_framework: str, code_to_test: str) -> str:
    """Return the prompt for the unit test."""
    return f"""{code_to_test}

# Unit tests for the above code using {unit_test_framework}:"""

def whole_code_prompt2(unit_test_framework: str, code_to_test: str) -> str:
    """Return the prompt for the unit test."""
    return f"""{code_to_test}

# Unit tests for the above code using {unit_test_framework}. Be sure to effectively sample from the input space, considering equivalence partitioning, boundary analysis, and other best testing practice."""

def whole_code_prompt3(unit_test_framework: str, code_to_test: str) -> str:
    """Return the prompt for the unit test."""
    return f"""{code_to_test}\n\n### Unit tests for the above files using {unit_test_framework}. Make sure they are concise and complete. ###\n\n"""

def single_function_prompt(unit_test_framework: str, code_to_test: str) -> str:
    """Return the prompt for the unit test."""
    return f"""{code_to_test}

# Unit tests for the above code using {unit_test_framework}:"""

def split_into_functions(code: str) -> list:
    """Split the code into a list of functions/classes."""

    # TODO: This can be much smarter.
    # Should act like a tokenizer, going line by line, checking for starting def/class and following until whitespace is what you expect.
    return list(map(lambda f: "class " + f, code.split("class ")))

def validate_tests(test_code: str) -> bool:
    """Check that the tests are valid."""
    pass

def write_to_file(code_to_test: str, test_code: str, file_name: str):
    """Write the test code to a file."""
    with open(file_name, "w") as f:
        f.write(code_to_test + "\n\n")
        f.write(test_code)


## PIPELINES ##

"""Here we write a series of pipelines to see which works best.
Different combinations of code splitting and context injection, different prompts, deterministic checkers/editors, etc."""
def naive_pipeline(unit_test_framework: str, code_to_test: str, llm: LLM):
    """Generate unit tests in a single prompt."""
    prompt = whole_code_prompt3(unit_test_framework, code_to_test)
    completion = llm.complete(prompt, max_tokens=500)
    return completion


def better_pipeine(unit_test_framework: str, code_to_test: str, llm: LLM):
    """Split into functions and complete for each separately, no context."""
    functions = split_into_functions(code_to_test)

    tests = []

    for function in functions:
        prompt = single_function_prompt(unit_test_framework, function)
        completion = llm.complete(prompt, max_tokens=200)
        tests.append(completion)

    # May want to deduplicate any overhead code that it writes, or maybe it won't write any, we'll have to add separately.
    
    return "\n\n".join(tests)

def even_better_pipeline(unit_test_framework: str, code_to_test: str, llm: LLM):
    """Split into functions and complete for each separately, adding context determined by analyzing dependencies in the code (which variables are used)."""
    pass



if __name__ == "__main__":
    # Flow with OpenAI Codex

    llm = OpenAI(engine=tuned_model)
    prompts = []
    directory = "dlt_code"
    file_names = os.listdir(directory)
    for file_name in file_names:
        code_to_test = open(directory + "/" + file_name, "r").read()
        compressed = c_p(code_to_test, file_name)

        prompts.append(compressed)

    completions = llm.parallel_complete(prompts, max_tokens=1024, stop=["<|endoftext|>"])
    
    for i in range(len(file_names)):
        file_name = file_names[i]
        completion = completions[i]
        code_to_test = open(directory + "/" + file_name, "r").read()
        write_to_file(code_to_test, completion, "tests/" + file_name)

    # Flow with Salesforce Codegen
    
    # llm = HuggingFace("microsoft/CodeGPT-small-py")
    # for file_name in os.listdir("code"):
    #     code_to_test = open("code/" + file_name, "r").read()
    #     completion = naive_pipeline("pytest", code_to_test, llm)
    #     write_to_file("", completion, "tests/" + file_name)
    #     print("Wrote to file: " + file_name)
