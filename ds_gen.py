import os
import ast
import docstring_parser
import typer
from llm import OpenAI
from prompts import SimplePrompter

app = typer.Typer()
gpt = OpenAI()

CURIE_FINE_TUNE = "curie:ft-personal-2023-01-03-17-34-19"
DAVINCI_FINE_TUNE = "davinci:ft-personal:docstring-completions-davinci-1-2023-01-03-18-02-05"

fn_prompter = SimplePrompter(lambda fn: ast.unparse(fn) + "\n\n###\n\n")

def write_ds_for_fn(fn: ast.FunctionDef, format: docstring_parser.DocstringStyle=docstring_parser.DocstringStyle.GOOGLE):
    """Write a docstring for a function"""

    # If it already has a docstring, skip it
    if ast.get_docstring(fn):
        return None
    
    prompt = ast.unparse(fn) + "\n\n###\n\n" # + "\n\nWrite a docstring for the above function:\n\n"
    completion = gpt.complete(prompt, model=DAVINCI_FINE_TUNE, stop=["END"]).strip() # .replace('"""', '').strip() # Remove leading/trailing newline

    # Convert to Docstring, and render back in the desired format, padding with necessary newlines, quotes, and indentation
    ds = docstring_parser.parse(completion)
    rendered = docstring_parser.compose(ds, format)
    return '    """\n    ' + rendered.replace("\n", "\n\t") + '\n    """\n'

def write_ds_for_class(cls: ast.ClassDef, format: docstring_parser.DocstringStyle=docstring_parser.DocstringStyle.GOOGLE):
    """Write a docstring for a class"""

    # If it already has a docstring, skip it
    if ast.get_docstring(cls):
        return None
    
    # Generate a summary of the class as a whole
    prompt = ast.unparse(cls) + "\n\n###\n\nWrite a summary of the above class:" # + "\n\nWrite a docstring for the above class:\n\n"
    summary = gpt.complete(prompt, model=DAVINCI_FINE_TUNE, stop=["END"]).strip() # .replace('"""', '').strip() # Remove leading/trailing newline

    # Generate the rest of the docstring, because it is just based on functions and attributes
    methods = list(filter(lambda x: isinstance(x, ast.FunctionDef) or isinstance(x, ast.AsyncFunctionDef), cls.body))
    attrs = list(filter(lambda x: isinstance(x, ast.Assign), cls.body))
    # TODO: Use the above to write the rest of the docstring

    # Write the docstrings for the methods
    method_to_ds = {}
    for method in methods:
        ds = write_ds_for_fn(method, format=format)
        if ds is not None:
            method_to_ds[method.name] = ds

    ds = summary

    return '    """\n    ' + ds.replace("\n", "\n\t") + '\n    """\n', method_to_ds

docstring_formats = {
    "google": docstring_parser.DocstringStyle.GOOGLE,
    "numpy": docstring_parser.DocstringStyle.NUMPYDOC,
    "epytext": docstring_parser.DocstringStyle.EPYDOC,
    "rest": docstring_parser.DocstringStyle.REST
}

def write_ds_for_string(code: str, double: bool=False, format: str="google"):
    """Write docstrings for all functions in a file"""

    # Parse all top-level functions+classes from file
    tree = ast.parse(code)

    # Write docstring for each
    fn_to_ds = {}
    cls_to_ds = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            ds = write_ds_for_fn(node, format=docstring_formats[format])
            if ds is not None:
                fn_to_ds[node.name] = ds
        elif isinstance(node, ast.ClassDef):
            ds, method_to_ds = write_ds_for_class(node, format=docstring_formats[format])
            fn_to_ds.update(method_to_ds)
            if ds is not None:
                cls_to_ds[node.name] = ds
        
    # Rewrite file with docstrings
    lines = code.split("\n")
    
    new_lines = []
    in_class = False
    for line in lines:
        new_lines.append(line)

        # Keep track of class so we know to write docstrings for indented methods
        if line.startswith("class "):
            in_class = True
            cls_name = line.split("class ")[1].split(":")[0]
            if cls_name in cls_to_ds:
                new_lines.append(cls_to_ds[cls_name])

        if line.startswith("def ") or line.startswith("async def ") or (in_class and line.startswith("    def ")) or (in_class and line.startswith("    async def ")):
            fn_name = line.strip().split("def ")[1].split("(")[0]
            if fn_name in fn_to_ds:
                new_lines.append(("    " if in_class else "") + fn_to_ds[fn_name])
    
    return new_lines

def write_ds_for_file(input: str, output: str, double: bool=False, format: str="google"):
    """Write docstrings for all functions in a file"""

    # Parse all top-level functions+classes from file
    with open(input, "r") as f:
        code = f.read()
    
    new_lines = write_ds_for_string(code, double=double, format=format)
    
    with open(output, "w") as f:
        f.writelines(new_lines)

def write_ds_for_folder(input: str, output: str, double: bool=False, format: str="google", recursive: bool=True):
    """Write docstrings for all functions in a folder"""

    for _, _, files in os.walk(input):
        for file in files:
            if file.endswith(".py"):
                print("Writing docstrings for", file, "...")
                write_ds_for_file(input + "/" + file, output + "/" + file, double=double, format=format)


@app.command()
def write_ds(input: str, output: str, double: bool=False, format: str="google", recursive: bool=True):
    """Write docstrings for all functions in a file or folder"""

    if os.path.isdir(input):
        assert os.path.isdir(output), "Output must be a directory if input is a directory"
        write_ds_for_folder(input, output, double=double, format=format, recursive=recursive)
    else:
        write_ds_for_file(input, output, double=double, format=format)

if __name__ == "__main__":
    app()