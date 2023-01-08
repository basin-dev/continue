from datasets import load_dataset
from data_tools import *
from parse import *
from tqdm import tqdm
import docstring_parser
import json

dataset = load_dataset("bigcode/the-stack", data_dir="data/python", streaming=True, split="train")

def docstring_is_quality(tree: ast.ClassDef | ast.FunctionDef, docstring: str) -> bool:
    """Determine whether a docstring is of high quality."""
    parsed = docstring_parser.parse(docstring)

    if isinstance(tree, ast.FunctionDef):
        # Check that the docstring has the right number of arguments
        num_args = len(tree.args.args)
        if len(parsed.params) != num_args:
            return False
        
        # Check that the docstring has a return type
        if parsed.returns is None:
            return False

    # Check that it has a description
    if parsed.short_description is None and parsed.long_description is None:
        return False

    return True

n = 1000
max_tokens = 2048
completions = []
for i, example in tqdm(enumerate(dataset)):
    if i >= n:
        break

    try:
        tree = parse_text(example['content'])
    except:
        continue

    # Only functions for now. Classes should have all of their methods documented and the rest can be done deterministically, other than description of the class.
    fcs = list(filter(lambda t: isinstance(t, ast.FunctionDef), tree.body))
    for fc in fcs:
        docstring = ast.get_docstring(fc)

        if docstring is not None and docstring_is_quality(fc, docstring):
            completion = fc.body.pop(0).value.value
            prompt = ast.unparse(fc)

            if count_tokens(prompt + completion) > max_tokens:
                continue

            completions.append({
                "prompt": prompt,
                "completion": completion + "END"
            })

with open("docstring_completions.json", "w") as f:
    json.dump(completions, f)