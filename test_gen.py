import ast
import os
from typing import Any, Dict, List, Tuple
from llm import OpenAI, count_tokens
import pytest
import json
import prompts
import pytest_parse

gpt = OpenAI()

def get_code(file_path: str):
    """Get the code for all functions and class methods in the file."""

    with open(file_path, 'r') as file:
        tree = ast.parse(file.read())

    functions = []
    classes = []
    for node in tree.body: # Only traverses top-level nodes

        if isinstance(node, ast.FunctionDef):
            functions.append(ast.unparse(node))

        elif isinstance(node, ast.ClassDef):
            classes.append({'name': node.name, 'methods': []})
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name == "__init__":
                    classes[-1]['init'] = ast.unparse(child)
                else:
                    classes[-1]['methods'].append(ast.unparse(child))

    return functions, classes

# a function to iterate through all files in the directory
def iterate_files(dir: str):
    """Iterate through all files in the directory."""
    dir_code = []
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.startswith("test"):
                continue
            if file.endswith(".py") and file != "__init__.py" and file != "__temp__.py":
                dir_code.append({'name': file})
                dir_code[-1]['functions'], dir_code[-1]['classes'] = get_code(os.path.join(root, file))
    
    return dir_code

temp_id = 0 # Write to different filenames to avoid overlap problems
def write_tests_to_file(tests: List[str], code_path: str, temp: bool=False) -> str:
    """Write the tests, returning the path they were written to."""
    code_dir, code_file = os.path.split(code_path)
    global temp_id
    test_file_name = f"test_{code_file}" if not temp else f"__temp__{temp_id}.py"
    temp_id += 1
    test_file_path = os.path.join(code_dir, "tests/", test_file_name)

    # Preliminary write, test by test
    with open(test_file_path, 'w') as output:
        for test in tests:
            output.write(test.strip() + "\n\n")
        
    # Capture all imports to deduplicate and move to top
    with open(test_file_path, 'r') as output:
        new_lines = []
        imports = set(["import pytest\n", f"from ..{code_file.split('.')[0]} import *\n"])
        for line in output.readlines():
            if line.startswith("import") or line.startswith("from"):
                imports.add(line.strip() + "\n")
            else:
                new_lines.append(line)
    

    # Write everything to file
    with open(test_file_path, "w") as output:
        output.write("# Generated test file for " + code_file + "\n\n")
        output.writelines(imports)
        output.write("\n\n")
        output.writelines(new_lines)

    return test_file_path

def validate_test_parses(test: str, max_tokens=512):
    """Validate that the code is a valid test. If length is at max_tokens and doesn't parse, then completion probably cut short."""
    try:
        ast.parse(test)
    except SyntaxError:
        if count_tokens(test) - max_tokens < 2: # idk if it would ever stop a few short, so gave some buffer
            print("Code didn't parse and hit max_tokens. This probably means that the completion was cut short.")
        return False

    return True

def validate_test_runs(test: str, file_path: str):
    """Validate that the code runs, and if so check if it passed.
        True for pass, False for not pass, None for doesn't run."""
    test_file_path = write_tests_to_file([test], file_path, temp=True)
    try:
        res = pytest.main([test_file_path, "-qqq"])

        if res is pytest.ExitCode.OK:
            return True
        elif res is pytest.ExitCode.TESTS_FAILED:
            return False
        else:
            # One of: INTERNAL_ERROR, INTERRUPTED, NO_TESTS_COLLECTED, USAGE_ERROR
            return None
    except Exception as e:
        raise Exception("Pytest failed to run")
    finally:
        os.remove(test_file_path)

def throw_away_bad_tests(test: str, code_path: str) -> str | None:
    test_file_path = write_tests_to_file([test], code_path, temp=True)
    with open(test_file_path, "r") as f:
        test_code = f.read()

    statuses = pytest_parse.get_test_statuses(test_file_path)
    keep = [status == "." for status in statuses]
    # os.remove(test_file_path)

    tree = ast.parse(test_code)
    body = []
    i = 0
    found_keeper = False
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            if pytest_parse.find_decorator(node, "pytest.fixture") is not None:
                # Fixtures aren't tests
                body.append(node)
                continue
            
            if decorator := pytest_parse.find_decorator(node, "pytest.mark.parametrize"):
                # Check parametrizations one-by-one
                keepers = []
                for el in decorator.args[1].elts:
                    if keep[i]:
                        found_keeper = True
                        keepers.append(el)
                    i += 1
                if len(keepers) == 0:
                    # Throw out the whole function
                    continue
                else:
                    # Keep only good elements
                    decorator.args[1].elts = keepers
                    body.append(node)

            else:
                # Keep or throw out the whole function
                if keep[i]:
                    body.append(node)
                    found_keeper = True
                    i += 1

        elif isinstance(node, ast.ClassDef):
            # Check class methods
            keepers = []
            kept_test = False
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name.startswith("test_"):
                    if keep[i]:
                        keepers.append(child)
                        kept_test = True
                        found_keeper = True

                    i += 1
                else:
                    # Keep all non-functions
                    keepers.append(child)

            if not kept_test:
                # Throw out the whole class
                continue
            else:
                node.body = keepers
                body.append(node)
        
        else:
            # Keep everything that isn't a test
            body.append(node)
    
    if not found_keeper:
        return None

    return "\n\n".join([ast.unparse(node) for node in body])

def screen_for_parse(tests: List[str]) -> List[str]:
    """Screen for tests that parse."""
    return [test for test in tests if validate_test_parses(test)]

def screen_for_run_pass(tests: List[str], code_path: str) -> Tuple[List[str], List[str]]:
    """Screen for tests that run or pass."""
    ran = []
    passed = []
    for test in tests:
        try:
            passes = validate_test_runs(test, code_path)
            if passes:
                passed.append(test)
                ran.append(test)
            else:
                ran.append(test)
        except Exception as e:
            # print("Failed to run test: " + e)
            continue

    return ran, passed

def get_running_tests(tests: List[str], code_path: str) -> List[str]:
    """Validate a list of tests, displaying passing rates, and returning the running tests."""

    keepers = screen_for_parse(tests)
    ran, passed = screen_for_run_pass(keepers, code_path)
    
    print("Total tests:", len(tests))
    print("Parsed: ", len(keepers))
    print("Ran: ", len(ran))
    print("Passed: ", len(passed))
    
    return ran
        
def fuzz_test(code: str, test: str):
    with open("__temp__.py", "w") as f:
        f.write(code)
    write_tests_to_file([test], "__test_temp__.py")
    raise NotImplementedError # How to best create a safe environment for this... 

def get_lines_to_retry_for_coverage(fn: ast.FunctionDef | ast.AsyncFunctionDef, code_file_path: str, test_file_path: str) -> List[Tuple[int, str]] | None:
    """Check if the test should be retried for the given element to get more coverage. If so, return the lines that are uncovered and their contents."""
    LINE_RATIO_REQ = 0.5
    # BRANCH_RATIO_REQ = 0.0

    code_dir, code_file = os.path.split(code_file_path)
    test_dir, _ = os.path.split(test_file_path)
    
    # Generate and parse coverage.xml report
    cov_file = pytest_parse.run_coverage(test_dir, code_dir)
    _, uncovered_lines = pytest_parse.parse_cov_xml(cov_file, code_file)
    os.remove(cov_file)

    lines = pytest_parse.uncovered_lines_for_ast(code_file_path, fn, uncovered_lines)

    total_lines = fn.end_lineno - fn.lineno + 1
    if len(lines) / total_lines > LINE_RATIO_REQ:
        return None
    else:
        return lines

def generate_function_unit_tests(dir_code, code_dir):
    """Generate unit tests for all functions in the code directory."""
    for file in dir_code:
        
        # Write all function tests
        responses = prompts.SimplePrompter(prompts.general_1).parallel_complete(file['functions'])

        # Write all class tests
        cls_inps = []
        for cls in file['classes']:
            for method in cls['methods']:
                cls_inps.append([cls['name'], cls['init'], method])
        
        responses += prompts.SimplePrompter(lambda x: prompts.cls_1(x[0], x[1], x[2])).parallel_complete(cls_inps)

        # Validate so as to only write parsing, running, and passing tests
        code_path = os.path.join(code_dir, file['name'])
        responses = get_running_tests(responses, code_path)
        pruned_tests = list(filter(lambda x: x is not None, [throw_away_bad_tests(response, code_path) for response in responses])) # This actually prunes non-working tests
        print("Pruned: ", len(pruned_tests))
        write_tests_to_file(pruned_tests, code_path)

if __name__ == "__main__":
    """Get the code for all functions and class methods in the code directory."""
    code_dir = "./dlt_code"
    dir_code = iterate_files(code_dir)
    generate_function_unit_tests(dir_code, code_dir)