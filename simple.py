import ast
import os
from llm import OpenAI

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

def generate_function_unit_tests(dir_code, out_dir="./generated_tests"):
    """Generate unit tests for all functions in the code directory."""
    for file in dir_code:
        file_name = f'{out_dir}/test_{file["name"]}'
        
        # Write all function tests
        fn_prompts = [f"""{function}

# Write multiple Python unit tests using the pytest library for the above function, using parameterizations and doing a proper partitioning of the input space:"""
            for function in file['functions']]

        responses = gpt.parallel_complete(fn_prompts,
                model="text-davinci-003",
                temperature=0.7,
                max_tokens=512,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0)
        
        with open(file_name, 'a') as output:
            for response in responses:
                output.write(response.strip() + "\n\n")


        # Write all class tests
        cls_prompts = []
        for cls in file['classes']:
            for method in cls['methods']:
                prompt = f"""class {cls['name']}:
{cls['init']}
{method}

# Write multiple Python unit tests using the pytest library for the above class and its {method.split("def ")[1].split("(")[0]} method, using fixtures and parameterizations and doing a proper partitioning of the input space:"""
                cls_prompts.append(prompt)

        responses = gpt.parallel_complete(cls_prompts,
                model="text-davinci-003",
                temperature=0.7,
                max_tokens=512,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0)

        with open(file_name, 'a') as output:
            for response in responses:
                output.write(response.strip() + "\n\n")

        # Move all imports to the top
        with open(file_name, 'r') as output:
            new_lines = []
            imports = set()
            for line in output.readlines():
                if line.startswith("import") or line.startswith("from"):
                    imports.add(line)
                else:
                    new_lines.append(line)

        with open(file_name, "w") as output:
            output.write("# Generated test file for " + file['name'])
            output.writelines(imports)
            output.write(f"from ..{file['name'].split('.')[0]} import *")
            output.write("\n\n")
            output.writelines(new_lines)

if __name__ == "__main__":
    """Get the code for all functions and class methods in the code directory."""
    dir = "./dlt_code"
    dir_code = iterate_files(dir)
    generate_function_unit_tests(dir_code, out_dir="./dlt_code/tests")