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
    """Validate that the code runs, and if so check if it passed."""
    test_file_path = write_tests_to_file([test], file_path, temp=True)
    try:
        res = pytest.main([test_file_path, "-qqq"])
        if res == 0:
            return True
        else:
            return False
    except Exception as e:
        raise Exception("Pytest failed to run")
    finally:
        # os.remove(test_file_path)
        pass

def throw_away_bad_tests(test: str, code_path: str) -> str | None:
    test_file_path = write_tests_to_file([test], code_path, temp=True)
    with open(test_file_path, "r").read() as f:
        code = f.read()
    os.remove(test_file_path)

    statuses = pytest_parse.get_test_statuses(test_file_path)
    keep = [status == "." for status in statuses]

    tree = ast.parse(code)
    body = []
    i = 0
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            decorator = None
            for dec in node.decorator_list:
                if ast.unparse(dec).startswith("pytest.mark.parametrize"):
                    decorator = dec
                    break
            
            if decorator:
                # Check parametrizations one-by-one
                keepers = []
                for el in decorator.args[1].elts:
                    if keep[i]:
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
    
    if len(body) == 0:
        return None

    return "\n\n".join([ast.unparse(node) for node in body])

def validate_tests(tests: List[str], code_path: str, log=False) -> List[str]:
    """Validate a list of tests, displaying passing rates, and returning the passing tests."""

    no_parse = []
    no_run = []
    no_pass = []
    passed = []
    for test in tests:
        if not validate_test_parses(test):
            no_parse.append(test)
            continue

        try:
            passes = validate_test_runs(test, code_path)
            if not passes:
                no_pass.append(test)
            else:
                passed.append(test)
        except Exception as e:
            no_run.append(test)
    
    print("Total tests:", len(tests))
    print("Passing Tests:", len(passed))
    print("Failed to parse:", len(no_parse))
    print("Failed to run:", len(no_run))
    print("Did not pass:", len(no_pass))

    if log:
        with open("test_log.json", "w") as f:
            json.dump({
                "no_parse": no_parse,
                "no_run": no_run,
                "no_pass": no_pass,
            }, f)
    
    return passed
        
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
        passed = validate_tests(responses, code_path) # Just to print the stats
        print("All: ", len(responses))
        print("Passed: ", len(passed))
        pruned_tests = [throw_away_bad_tests(response, code_path) for response in responses] # This actually prunes non-working tests
        print("Pruned: ", len(pruned_tests))
        write_tests_to_file(pruned_tests, code_path)

if __name__ == "__main__":
    """Get the code for all functions and class methods in the code directory."""
    code_dir = "./dlt_code"
    dir_code = iterate_files(code_dir)
    generate_function_unit_tests(dir_code, code_dir)