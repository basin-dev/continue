from gpt_index import GPTSimpleVectorIndex, SimpleDirectoryReader
from typing import List
import os
import pathspec

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
    "**/coverage.xml"
]

def build_gitignore_spec(gitignore_paths: List[str]=None, custom_match_patterns: List[str]=[]) -> pathspec.PathSpec:
    """Build a pathspec.PathSpec from a given list of .gitignore files."""
    if gitignore_paths is None:
        gitignore_paths = upward_search_in_filetree(".gitignore", )


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

documents = SimpleDirectoryReader('data').load_data()
index = GPTSimpleVectorIndex(documents)
index.save_to_disk('index.json')
# index = GPTSimpleVectorIndex.load_from_disk('index.json')
response = index.query("What is sestinj working on right now?")
print(response)