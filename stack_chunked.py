# This is the same as stack.py, except we take a different approach
# Instead of shortening functions into signatures, just include all the code
# We chunk things instead in order to avoid token overflow
# For now we take the naive chunking approach, with basically a sliding window
# that makes sure not to cut off functions or classes

# But how do we assign labels to these chunks?

import json
from datasets import load_dataset
from data_tools import *
from parse import *
from tqdm import tqdm
from matplotlib import pyplot as plt

f = open("completions.json", "r")
cached_completions = json.load(f)
f.close()

if len(cached_completions) and 'repo' in cached_completions[0]:
    cached_completion_repos = set(map(lambda c: c['repo'], cached_completions))
else:
    cached_completion_repos = set()

# dataset = load_dataset("bigcode/the-stack-smol", data_dir="data/python")['train']
dataset = load_dataset("bigcode/the-stack", data_dir="data/python", streaming=True, split="train")

good = []
files_by_repository = {}

i = 0
desired_examples = 200

j = 0
offset = 0

for example in iter(dataset):
    if j < offset:
        j += 1
        continue

    if example['max_stars_repo_name'] in cached_completion_repos:
        continue

    content = example['content']
    if 'pytest' in content:
        good.append(example)

    repo = example['max_stars_repo_name']
    if repo not in files_by_repository:
        files_by_repository[repo] = []
    files_by_repository[repo].append(example)

    i += 1
    if i >= desired_examples:
        break

with_pytest = list(filter(lambda f: 'import pytest' in f['content'], good))
repos_with_pytest = list(set(map(lambda f: f['max_stars_repo_name'], with_pytest)))

default_file_contents = """import pytest\n\n"""

def remove_copyright(contents: str) -> str:
    """Remove the copyright header from a file."""
    lines = contents.splitlines()
    lines = list(filter(lambda l: l.startswith("__copyright__") or l.startswith("__license__"), lines))

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

no_paths_count = 0
missing_file_count = 0
missing_paths = []

def compile_completion(file):
    """Compile a completion from a file."""
    if file['max_stars_repo_name'] in cached_completion_repos:
        return None

    global no_paths_count, missing_file_count

    deps = find_import_dependencies(file['content'])
    paths = dependency_paths(file['max_stars_repo_path'], deps, file['max_stars_repo_name'])

    if len(paths) == 0:
        # print("No paths found with deps ", file['max_stars_repo_name'], deps)
        no_paths_count += 1
        missing_paths.append((file, deps))
        return None
    
    headers = []
    header_names = []
    missed_file = False
    for path in paths:
        resp = gh_raw(file['max_stars_repo_name'], path)
        if resp.status_code == 404:
            missed_file = True
            continue

        headers.append(resp.text)
        header_names.append(path)

    if missed_file:
        # print("Missed a file.")
        missing_file_count += 1
        # return None
    if len(headers) == 0:
        print("No files found.")
        return None

    prompt = ""
    for i in range(len(headers)):
        prompt += f"\n\n### {header_names[i]} ###\n\n"
        prompt += headers[i]

    # Now compress into function signatures
    try:
        ass_tree = parse_text(prompt)
        sigs = get_signatures(ass_tree)
        if len(sigs) == 0:
            return None
    except:
        print("Failed to parse.")
        return None

    prompt = "\n\n".join(sigs)
    prompt += "\n\n###\n\n" # Unit tests for the above files using pytest. Make sure they are concise and complete. ###\n\n"

    completion = remove_copyright(file['content']) + "<|endoftext|>"
    
    return {
        "prompt": prompt,
        "completion": completion,
        "repo": file['max_stars_repo_name'],
    }

completions = cached_completions
print("Generating completions...")
n = len(with_pytest)
for file in tqdm(with_pytest[:int(n*1)]):
    completion = compile_completion(file)
    if completion is not None:
        completions.append(completion)

print(f"Generated {len(completions)} completions out of {len(with_pytest)} files with pytest out of {desired_examples} total examples.")
print(f"Missed {no_paths_count} files due to missing dependencies.")
print(f"Missed {missing_file_count} files due to missing files.")

# print("These were all the missing imports: ", missed_imports)

prompt_lengths = []
completion_lengths = []
for completion in completions:
    prompt_lengths.append(count_tokens(completion['prompt']))
    completion_lengths.append(count_tokens(completion['completion']))


valid_completions = list(filter(lambda c: count_tokens(c["prompt"] + c["completion"]) < 2048, completions))
print("Percent of completions that are of valid length: ", str(len(valid_completions) / len(completions) * 100.0) + "%")


# plt.hist(prompt_lengths, bins=100)
# plt.title("Prompt lengths")
# plt.show()

# plt.hist(completion_lengths, bins=100)
# plt.title("Completion lengths")
# plt.show()

lens = list(map(lambda c: count_tokens(c["prompt"] + c["completion"]), completions))
plt.hist(lens, bins=100)
plt.title("Prompt+completion lengths")
plt.show()

with open("completions.json", "w") as f:
    print(f"Writing {len(valid_completions)} to completions to file...")
    json.dump(valid_completions, f)

all_text = "\n".join(list(map(lambda c: c["prompt"] + c["completion"], valid_completions)))
print("Total cost of fine-tuning:")
print("Davinci: ", price_per_token['davinci'] / 1000 * 4 * count_tokens(all_text))
print("Curie: ", price_per_token['curie'] / 1000 * 4 * count_tokens(all_text))