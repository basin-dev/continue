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
desired_examples = 5000

j = 0
offset = 66000

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
    if i == desired_examples:
        break

with_pytest = list(filter(lambda f: 'import pytest' in f['content'], good))
repos_with_pytest = list(set(map(lambda f: f['max_stars_repo_name'], with_pytest)))

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
    except:
        print("Failed to parse.")
        return None
    prompt = "\n\n".join(sigs)

    prompt += f"\n\n### Unit tests for the above files using pytest. Make sure they are concise and complete. ###\n\n"
    
    return {
        "prompt": prompt,
        "completion": file['content'] + "<|endoftext|>",
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