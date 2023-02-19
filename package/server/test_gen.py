import ast
import os
from typing import Any, Dict, List, Tuple

from pydantic import BaseModel

from package.libs.pytest_parse import find_decorator, get_test_statuses, parse_cov_xml, run_coverage, uncovered_lines_for_ast
from ..libs.language_models.llm import OpenAI, count_tokens
import pytest
from fastapi import APIRouter, HTTPException
from ..libs.language_models.prompts import BasicCommentPrompter, FormatStringPrompter, MixedPrompter, SimplePrompter, cls_1, cls_method_to_str

gpt = OpenAI()
router = APIRouter(prefix="/unittest", tags=["unittest"])

def get_code(filecontents: str):
    """Get the code for all functions and class methods in the file."""
    tree = ast.parse(filecontents)

    functions = []
    classes = []
    for node in tree.body: # Only traverses top-level nodes

        if isinstance(node, ast.FunctionDef):
            functions.append(node)

        elif isinstance(node, ast.ClassDef):
            classes.append({'name': node.name, 'methods': [], "node": node})
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name == "__init__":
                    classes[-1]['init'] = ast.unparse(child)
                else:
                    classes[-1]['methods'].append(child)

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
                filecontents = open(os.path.join(root, file), 'r').read()
                dir_code[-1]['functions'], dir_code[-1]['classes'] = get_code(filecontents)
    
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

def throw_away_bad_tests(test: str | None, code_path: str) -> str | None:
    if test is None:
        return None

    test_file_path = write_tests_to_file([test], code_path, temp=True)
    with open(test_file_path, "r") as f:
        test_code = f.read()

    try:
        statuses = get_test_statuses(test_file_path)
    except:
        # Probably an error in the test, nothing runs
        return None

    keep = [status == "." for status in statuses]
    # os.remove(test_file_path)

    tree = ast.parse(test_code)
    body = []
    i = 0
    found_keeper = False
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            if find_decorator(node, "pytest.fixture") is not None:
                # Fixtures aren't tests
                body.append(node)
                continue
            
            if decorator := find_decorator(node, "pytest.mark.parametrize"):
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
    return [
        test if validate_test_parses(test)
            else None
        for test in tests]

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
                passed.append(None)
        except Exception as e:
            # print("Failed to run test: " + e)
            ran.append(None)
            passed.append(None)

    return ran, passed

def count_not_none(l: List) -> int:
        return len([x for x in l if x is not None])

def get_running_tests(tests: List[str], code_path: str) -> List[str]:
    """Validate a list of tests, displaying passing rates, and returning the running tests."""

    keepers = screen_for_parse(tests)
    ran, passed = screen_for_run_pass(keepers, code_path)
    
    print("Total tests:", count_not_none(tests))
    print("Parsed: ", count_not_none(keepers))
    print("Ran: ", count_not_none(ran))
    print("Passed: ", count_not_none(passed))
    
    return ran
        
def fuzz_test(code: str, test: str):
    with open("__temp__.py", "w") as f:
        f.write(code)
    write_tests_to_file([test], "__test_temp__.py")
    raise NotImplementedError # How to best create a safe environment for this... 

def get_lines_to_retry_for_coverage(fn: ast.FunctionDef | ast.AsyncFunctionDef, code_file_path: str, test_file_path: str) -> List[Tuple[int, str]] | None:
    """Check if the test should be retried for the given element to get more coverage. If so, return the lines that are uncovered and their contents."""
    LINE_RATIO_REQ = 1.0
    # BRANCH_RATIO_REQ = 0.0

    code_dir, code_file = os.path.split(code_file_path)
    test_dir, _ = os.path.split(test_file_path)
    
    # Generate and parse coverage.xml report
    _, cov_file = run_coverage(test_dir, code_dir)
    _, uncovered_lines = parse_cov_xml(cov_file, code_file)
    os.remove(cov_file)

    lines = uncovered_lines_for_ast(code_file_path, fn, uncovered_lines)

    total_lines = fn.end_lineno - fn.lineno + 1
    if len(lines) / total_lines >= LINE_RATIO_REQ:
        return None
    else:
        return lines

def generate_function_unit_tests(dir_code, code_dir):
    """Generate unit tests for all functions in the code directory."""
    for file in dir_code:
        code_path = os.path.join(code_dir, file['name'])
        
        # Specify your prompts
        fn_prompter = BasicCommentPrompter("Write tests for the above code using pytest. Consider doing any of the following as needed: writing mocks, creating fixtures, using parameterization, setting up, and tearing down. All tests should pass:")
        cls_prompter = SimplePrompter(lambda x: cls_1(x[0]['name'], x[0]['init'], x[1]))
        prompter = MixedPrompter([fn_prompter, cls_prompter], lambda inp: 1 if isinstance(inp, list) and len(inp) == 2 else 0)

        # Chunk into methods of the class, gather all inputs
        cls_inps = []
        for cls in file['classes']:
            for method in cls['methods']:
                cls_inps.append([cls, ast.unparse(method)])

        all_inputs = list(map(lambda f: ast.unparse(f), file['functions'])) + cls_inps
        
        # Generate completions
        tests = prompter.parallel_complete(all_inputs)

        # Throughout this whole flow, we maintain a list of the same length, replacing elements with None instead of removing, in order to maintain order when retrying

        # Validate so as to only write parsing, running, and passing tests
        tests = get_running_tests(tests, code_path)
        tests = [throw_away_bad_tests(test, code_path) for test in tests]
        print("Pruned: ", count_not_none(tests))

        # First, retry for passing
        # Keep arrays of (index, test, input) for tests that need to be retried
        retry_for_pass = []
        for i, test in enumerate(tests):
            inp = all_inputs[i]
            if test is None:
                retry_for_pass.append((i, test, inp))

        rfp_inps = [el[2] for el in retry_for_pass]
        rfp_tests = prompter.parallel_complete(rfp_inps)
        rfp_tests = get_running_tests(rfp_tests, code_path)
        rfp_tests = [throw_away_bad_tests(test, code_path) for test in rfp_tests]
        for i, test in enumerate(rfp_tests):
            if test is not None and tests[i] is None:
                tests[i] = test

        # Then, retry for coverage
        retry_for_coverage = []
        for i, test in enumerate(tests):
            if test is None:
                continue

            inp = all_inputs[i]
            test_file_path = write_tests_to_file([test], code_path, temp=True)
            lines = get_lines_to_retry_for_coverage(inp, code_path, test_file_path)
            os.remove(test_file_path) # TODO: Make a testfile class where you can do a with statement for automatic cleanup
            if lines is not None:
                retry_for_coverage.append((i, test, inp, lines))

        def cov_prompt_fn(inp: Tuple[Any, List[str]]) -> str:
            """Prompt for retrying for coverage."""
            inp, lines = inp
            code = inp if type(inp) is str else cls_method_to_str(inp[0]['name'], inp[0]['init'], inp[1])
            lines = "\n# ".join(lines)
            return f"""{code}
        
# Write a python unit test for the above code using pytest, such that the following lines are covered:
# {lines} 

"""

        coverage_prompter = SimplePrompter(cov_prompt_fn)
        rfc_inps = [(el[2], el[3]) for el in retry_for_coverage]
        rfc_tests = coverage_prompter.parallel_complete(rfc_inps)
        rfc_tests = get_running_tests(rfc_tests, code_path)
        rfc_tests = [throw_away_bad_tests(test, code_path) for test in rfc_tests]
        for i, test in enumerate(rfc_tests):
            if test is not None:
                if tests[i] is None:
                    # Replace None with the new test
                    tests[i] = test
                else:
                    # Merge tests via concatenation
                    tests[i] += "\n\n" + test

        # Write all tests to file
        write_tests_to_file(tests, code_path)

class FilePosition(BaseModel):
    """A position in a file."""
    filecontents: str
    lineno: int

@router.post("/forline")
def forline(fp: FilePosition):
    """Write unit test for the function encapsulating the given line number."""
    functions, classes = get_code(fp.filecontents)
    ctx = None
    for function in functions:
        if function.lineno <= fp.lineno and function.end_lineno >= fp.lineno:
            ctx = ast.unparse(function)
            break
    if ctx is None:
        for cls in classes:
            for method in cls['methods']:
                if method.lineno <= fp.lineno and method.end_lineno >= fp.lineno:
                    ctx = (cls, method)
                    break
    
    if ctx is None:
        raise HTTPException(status_code=500, detail="No function or class method found at line number")

    print("ctx: ", ctx)
    
    fn_prompter = BasicCommentPrompter("Write tests for the above code using pytest. Consider doing any of the following as needed: writing mocks, creating fixtures, using parameterization, setting up, and tearing down. All tests should pass:")
    cls_prompter = SimplePrompter(lambda x: cls_1(x[0]['name'], x[0]['init'], ast.unparse(x[1])))
    prompter = MixedPrompter([fn_prompter, cls_prompter], lambda inp: 1 if isinstance(inp, tuple) and len(inp) == 2 else 0)

    print("PROMPT: ", prompter._compile_prompt(ctx)[0])

    test = prompter.complete(ctx)

    return {"completion": test.strip() + "\n\n"}

def file_position_to_code_str(fp: FilePosition) -> str | None:
    """Given a line in a file, find the most specific containing function, and return it as a string, including the class header if it's a method."""
    functions, classes = get_code(fp.filecontents)
    for function in functions:
        if function.lineno <= fp.lineno and function.end_lineno >= fp.lineno:
            return ast.unparse(function)

    for cls in classes:
        for method in cls['methods']:
            if method.lineno <= fp.lineno and method.end_lineno >= fp.lineno:
                return cls_method_to_str(cls['name'], cls['init'], method)

    return None

failing_test_prompter = FormatStringPrompter('''The is a description of my bug:

{description}

This is the code:

{code}

This is a failing pytest that will pass when the problem is solved:

''')

class FailingTestBody(BaseModel):
    """A failing test body."""
    description: str
    fp: FilePosition

@router.post("/failingtest")
def failingtest(body: FailingTestBody):
    """Write a failing test for the function encapsulating the given line number."""
    code = file_position_to_code_str(body.fp)
    if code is None:
        raise HTTPException(status_code=500, detail="No function or class method found at line number")

    test = failing_test_prompter.complete({"description": body.description, "code": code})
    return {"completion": test.strip() + "\n\n"}


if __name__ == "__main__":
    """Get the code for all functions and class methods in the code directory."""
    # code_dir = "./dlt_code"
    # dir_code = iterate_files(code_dir)
    # generate_function_unit_tests(dir_code, code_dir)

    # app()