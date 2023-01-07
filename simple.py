import ast
import os
import openai

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
            if file.endswith(".py"):
                dir_code.append({'name': file})
                dir_code[-1]['functions'], dir_code[-1]['classes'] = get_code(os.path.join(root, file))
    
    return dir_code

def generate_function_unit_tests(dir_code, out_dir="./generated_tests"):
    """Generate unit tests for all functions in the code directory."""
    for file in dir_code:
        with open(f'{out_dir}/test_{file["name"]}', 'w') as output:
            output.write("import pytest")

        for function in file['functions']:
            prompt = f"""{function}

# Write multiple Python unit tests using the pytest library for the above function, using parameterizations and doing a proper partitioning of the input space:"""

            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                temperature=0.7,
                max_tokens=512,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )['choices'][0]['text']

            with open(f'{out_dir}/test_{file["name"]}', 'a') as output:
                output.write(response.replace("import pytest\n", "") + "\n\n")

if __name__ == "__main__":
    """Get the code for all functions and class methods in the code directory."""
    dir = "./dlt_code"
    dir_code = iterate_files(dir)

    generate_function_unit_tests(dir_code)