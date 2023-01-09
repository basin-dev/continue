import ast
import os
from typing import List
from llm import OpenAI
import pytest
import json
import prompts

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
            if file.endswith(".py"):
                dir_code.append({'name': file})
                dir_code[-1]['functions'], dir_code[-1]['classes'] = get_code(os.path.join(root, file))
    
    return dir_code

def write_tests_to_file(tests: List[str], path: str):
    """Write the tests to the file."""

    # Preliminary write, test by test
    with open(path, 'a') as output:
        for test in tests:
            output.write(test.strip() + "\n\n")
        
    # Capture all imports to deduplicate and move to top
    with open(path, 'r') as output:
        new_lines = []
        imports = set(["import pytest"])
        for line in output.readlines():
            if line.startswith("import") or line.startswith("from"):
                imports.add(line)
            else:
                new_lines.append(line)

    # Write everything to file
    file_name = path.split("/")[-1]
    with open(path, "w") as output:
        output.write("# Generated test file for " + file_name)
        output.writelines(imports)
        output.write(f"from ..{file_name.split('.')[0]} import *")
        output.write("\n\n")
        output.writelines(new_lines)


def validate_test_parses(code: str):
    """Validate that the code is a valid test."""
    try:
        ast.parse(code)
    except SyntaxError:
        return False

    return True

def validate_test_runs(code: str):
    """Validate that the code runs, and if so check if it passed."""

    write_tests_to_file([code], "__temp__.py")

    try:
        res = pytest.main(["__temp__.py"])
        if res == 0:
            return True
        else:
            return False
    except Exception:
        raise Exception("Pytest failed to run")
    finally:
        os.remove("__temp__.py")

def validate_tests(tests: List[str], log=False):
    """Validate a list of tests, displaying passing rates."""

    no_parse = []
    no_run = []
    no_pass = []
    passed = 0
    for test in tests:
        if not validate_test_parses(test):
            no_parse.append(test)
            continue
        try:
            passes = validate_test_runs(test)
            if not passes:
                no_pass.append(test)
            else:
                passed += 1
        except:
            no_run.append(test)
    
    print("Total tests:", len(tests))
    print("Passing Tests:", passed)
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
        

def generate_function_unit_tests(dir_code, out_dir="./generated_tests"):
    """Generate unit tests for all functions in the code directory."""
    for file in dir_code:
        
        # Write all function tests
        fn_prompts = [prompts.fn_1(fn_code) for fn_code in file['functions']]

        responses = gpt.parallel_complete(fn_prompts,
                model="text-davinci-003",
                temperature=0.7,
                max_tokens=512,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0)


        # Write all class tests
        cls_prompts = []
        for cls in file['classes']:
            for method in cls['methods']:
                prompt = prompts.cls_1(cls['name'], cls['init'], method)
                cls_prompts.append(prompt)

        responses += gpt.parallel_complete(cls_prompts,
                model="text-davinci-003",
                temperature=0.7,
                max_tokens=512,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0)
        
        validate_tests(responses, log=True)
        write_tests_to_file(responses, f'{out_dir}/test_{file["name"]}')

if __name__ == "__main__":
    """Get the code for all functions and class methods in the code directory."""
    dir = "./dlt_code"
    dir_code = iterate_files(dir)
    generate_function_unit_tests(dir_code, out_dir="./dlt_code/tests")