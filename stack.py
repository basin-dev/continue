import json
from datasets import load_dataset
from data_tools import *
from parse import *
from tqdm import tqdm
from matplotlib import pyplot as plt

dataset = load_dataset("bigcode/the-stack-smol", data_dir="data/python")['train']

good = []
files_by_repository = {}
for example in dataset:
    content = example['content']
    if 'pytest' in content:
        good.append(example)

    repo = example['repository_name']
    if repo not in files_by_repository:
        files_by_repository[repo] = []
    files_by_repository[repo].append(example)

with_pytest = list(filter(lambda f: 'import pytest' in f['content'], good))
repos_with_pytest = list(set(map(lambda f: f['repository_name'], with_pytest)))

default_file_contents = """import pytest\n\n"""

def remove_copyright(contents: str) -> str:
    """Remove the copyright header from a file."""
    lines = contents.splitlines()

    # Find the top comment block. This is usually what contains the copyright.
    non_block_lines = []
    block_lines = []
    comment_block_started = False
    comment_block_ended = False
    for line in lines:
        if comment_block_ended:
            non_block_lines.append(line)
        elif line.strip().startswith('#'):
            comment_block_started = True
            block_lines.append(line)
        elif comment_block_started:
            comment_block_ended = True
            non_block_lines.append(line)

    block = "\n".join(block_lines)

    # Determine if the block should be discarded
    if "Copyright" in block or "License" in block:
        return "\n".join(non_block_lines)
    else:
        return "\n".join(block_lines + non_block_lines)

def clean_file(contents: str) -> str:
    """Remove unnecessary import and comments from a file."""
    contents = remove_copyright(contents)

    lines = contents.splitlines()
    new_lines = []
    for line in lines:
        if line.startswith('import') or line.startswith("from"):
            continue
        new_lines.append(line)
    return "\n".join(new_lines)

def compile_completion(file):
    deps = find_import_dependencies(file['content'])
    paths = dependency_paths(file['path'], deps, file['repository_name'])

    if len(paths) == 0:
        # print("No paths found with deps ", file['repository_name'], deps)
        return None
    
    headers = []
    header_names = []
    missed_file = False
    for path in paths:
        resp = gh_raw(file['repository_name'], path)
        if resp.status_code == 404:
            missed_file = True
            break

        headers.append(resp.text)
        header_names.append(path)

    if missed_file:
        # print("Missed a file.")
        return None

    prompt = ""
    for i in range(len(headers)):
        prompt += f"\n\n### {header_names[i]} ###\n\n"
        prompt += headers[i]

    # Now compress into function signatures
    sigs = get_signatures(parse_text(prompt))
    prompt = "\n\n".join(sigs)

    prompt += f"\n\n### Unit tests for the above files using pytest. Make sure they are concise and complete. ###\n\n"
    
    return {
        "prompt": prompt,
        "completion": file['content'] + "<|endoftext|>"
    }

completions = []
print("Generating completions...")
n = len(with_pytest)
for file in tqdm(with_pytest):
    completion = compile_completion(file)
    if completion is not None:
        completions.append(completion)

print(f"Generated {len(completions)} completions.")


prompt_lengths = []
completion_lengths = []
for completion in completions:
    prompt_lengths.append(count_tokens(completion['prompt']))
    completion_lengths.append(count_tokens(completion['completion']))

plt.hist(prompt_lengths, bins=100)
plt.title("Prompt lengths")
plt.show()

plt.hist(completion_lengths, bins=100)
plt.title("Completion lengths")
plt.show()

# Uncomment this to manually check the completions
# passed = []
# for c in completions:
#     print("\n\n======================================================================================================\n======================================================================================================\n\n")
#     print(c['prompt'])
#     print(c['completion'])
#     inp = input("Pass? (y/n): ")
#     if inp.lower() == "y":
#         passed.append(c)

with open("pytest_files.json", "w") as f:
    json.dump(completions, f)