from typing import List
import pathspec
from gpt_index import GPTSimpleVectorIndex, Document
import subprocess
import os
import re

def get_modified_files() -> List[str]:
    """Get a list of all files that have been modified since the last commit."""

    # Get the current commit
    current_commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()

    # Get the parent commit
    parent_commit = subprocess.check_output(["git", "rev-parse", "HEAD^"]).decode("utf-8").strip()

    # Get the list of files that have been modified
    modified_files = subprocess.check_output(["git", "diff", "--name-only", parent_commit, current_commit]).decode("utf-8").strip()

    # Split the output into lines
    modified_files = modified_files.split("\n")

    # Remove empty lines
    modified_files = [f for f in modified_files if f]

    # Get the list of files that have been deleted
    deleted_files = [f for f in modified_files if not os.path.exists(f)]

    # Remove deleted files from the list
    modified_files = [f for f in modified_files if os.path.exists(f)]

    print(modified_files)
    print(deleted_files)

    return modified_files, deleted_files

def update_file_index(gitignore_spec: pathspec.PathSpec, index: GPTSimpleVectorIndex):
    """Update the index with a list of files."""
    files = get_modified_files()
    for file in files:
        if not gitignore_spec.match_file(file):
            index.add_document(Document(file, file))
        else:
            print(f"Skipping {file} because it is ignored by .gitignore")

get_modified_files()