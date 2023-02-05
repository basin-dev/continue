import faiss
import json
import os
import pathspec
import subprocess

from gpt_index import GPTSimpleVectorIndex, SimpleDirectoryReader, Document, GPTFaissIndex
from typing import List, Generator


DEFAULT_GIT_IGNORE_PATTERNS = [
    "**/.env",
    "**/env",
    "**/venv",
    "**/node_modules",
    "**/__pycache__",
    "**/dist",
    "**/build",
    "**/.pytest_cache",
    "**/.mypy_cache",
    "**/.coverage",
    "**/.DS_Store",
    "**/coverage.xml",
    "**/bin/**",
    "**/opt/**",
    "**/env/**"
    "autodebug/scripts/data/**"
]


def upward_search_in_filetree(search_for: str, start_path: str=".") -> List[str]:
    """Find all files of the name search_for in parent directories of the given path."""
    found = []
    while True:
        # Check whether there is a file named search_for here
        target_file_path = os.path.join(start_path, search_for)
        if os.path.exists(target_file_path):
            found.append(target_file_path)
        
        parent_dir = os.path.abspath(os.path.join(start_path, os.pardir))
        if parent_dir == start_path:
            # Reached root
            break

        # Move up one directory
        start_path = parent_dir

    return found


def build_gitignore_spec(gitignore_paths: List[str]=None, custom_match_patterns: List[str]=[]) -> pathspec.PathSpec:
    """Build a pathspec.PathSpec from a given list of .gitignore files."""
    if gitignore_paths is None:
        gitignore_paths = upward_search_in_filetree(".gitignore", ".")

    # Acculumate lines from all .gitignore files
    lines = set(custom_match_patterns)
    for gitignore_path in gitignore_paths:
        try:
            with open(gitignore_path, "r") as f:
                lines.update(f.readlines())
        except BaseException:
            # Don't throw if the file doesn't exist
            pass
    
    # Negate all line, except for comments and empty lines, because we want to ignore them
    lines = [f"!{line}" for line in lines if not line.startswith("#") and line.strip() != ""]

    return pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, lines)


def load_gpt_index_documents(root: str) -> List[Document]:
    """Loads a list of GPTIndex Documents, respecting .gitignore files."""
    # Build a pathspec.PathSpec from the .gitignore files
    gitignore_spec = build_gitignore_spec()
    # Walk the root directory to get a list of all non-ignored files
    input_files = gitignore_spec.match_tree_files(root)
    # Use SimpleDirectoryReader to load the files into Documents
    return SimpleDirectoryReader(root, input_files=input_files).load_data()


def create_file_index():
    """Create a new index for the current branch."""
    branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode("utf-8").strip()
    if not os.path.exists("data/{branch}"):
        os.makedirs(f"data/{branch}")

    d = 1536 # Dimension of text-ada-embedding-002
    faiss_index = faiss.IndexFlatL2(d)
    documents = load_gpt_index_documents("/Users/ty/Documents/nate-ty-side-projects/unit-test-experiments/")
    index = GPTFaissIndex(documents, faiss_index=faiss_index)
    index.save_to_disk(f"data/{branch}/index.json")
    with open(f"data/{branch}/metadata.json", "w") as f:
        f.write(json.dumps({"commit": subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()}))
    print("Codebase index created")


def get_modified_deleted_files():
    """Get a list of all files that have been modified since the last commit."""
    branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode("utf-8").strip()
    current_commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()

    metadata = "data/{branch}/metadata.json"
    with open(metadata, "r") as f:
        previous_commit = f.read()["commit"]

    modified_deleted_files = subprocess.check_output(["git", "diff", "--name-only", previous_commit, current_commit]).decode("utf-8").strip()
    modified_deleted_files = modified_deleted_files.split("\n")
    modified_deleted_files = [f for f in modified_deleted_files if f]

    deleted_files = [f for f in modified_deleted_files if not os.path.exists(f)]
    modified_files = [f for f in modified_deleted_files if os.path.exists(f)]

    with open(metadata, "w") as f:
        f.write({"commit": current_commit})

    return modified_files, deleted_files


def update_codebase_index():
    """Update the index with a list of files."""
    branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode("utf-8").strip()
    gitignore_spec = build_gitignore_spec(custom_match_patterns=DEFAULT_GIT_IGNORE_PATTERNS)

    if not os.path.exists(f"data/{branch}"):
        create_file_index()
    else:
        index = GPTFaissIndex.load_from_disk(f"data/{branch}/index.json")
        modified_files, deleted_files = get_modified_deleted_files()
        for file in modified_files:
            if not gitignore_spec.match_file(file):
                index.update(file)
            else:
                print(f"Skipping {file} because it is ignored by .gitignore")
        for file in deleted_files:
            index.delete(file)
        print("Codebase index updated")


if __name__ == "__main__":
    """python3 update.py"""
    update_codebase_index()