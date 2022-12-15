from datasets import load_dataset

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