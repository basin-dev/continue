import json
from datasets import load_dataset
from data_tools import *
from tqdm import tqdm

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


def compile_completion(file):
    deps = find_import_dependencies(file['content'])
    paths = dependency_paths(file['path'], deps, file['repository_name'])

    if len(paths) == 0:
        print("No paths found with deps ", file['repository_name'], deps)
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
        print("Missed a file.")
        return None

    prompt = ""
    for i in range(len(headers)):
        prompt += f"\n\n### {header_names[i]} ###\n\n"
        prompt += headers[i]

    prompt += f"\n\n### Unit tests for the above files using pytest. Make sure they are concise and complete. ###\n\n"
    
    return {
        "prompt": prompt,
        "completion": file['content']
    }

completions = []
print("Generating completions...")
for file in tqdm(with_pytest):
    completion = compile_completion(file)
    if completion is not None:
        completions.append(completion)

print(f"Generated {len(completions)} completions.")

passed = completions # []
# for c in completions:
#     print("\n\n======================================================================================================\n======================================================================================================\n\n")
#     print(c['prompt'])
#     print(c['completion'])
#     inp = input("Pass? (y/n): ")
#     if inp.lower() == "y":
#         passed.append(c)

with open("pytest_files.json", "w") as f:
    json.dump(passed, f)