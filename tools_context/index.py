from gpt_index import GPTSimpleVectorIndex, SimpleDirectoryReader, Document, GPTFaissIndex
from typing import List, Generator
import pathspec
import os
import faiss # https://github.com/facebookresearch/faiss/blob/main/INSTALL.md

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
    "**/coverage.xml",
    "**/bin/**",
    "**/opt/**",
    "**/env/**"
    "autodebug/data/**"
]

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
    return SimpleDirectoryReader(rot, input_files=input_files).load_data()

documents = load_gpt_index_documents("data")
d = 1536 # Dimension of text-ada-embedding-002
faiss_index = faiss.IndexFlatL2(d)
index = GPTFaissIndex(documents, faiss_index=faiss_index)
index.save_to_disk('file_index.json')
# index = GPTSimpleVectorIndex.load_from_disk('index.json')
response = index.query("What is sestinj working on right now?")
print(response)