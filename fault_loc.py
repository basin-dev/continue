from typing import Callable, Dict, List, Tuple
from boltons import tbutils
import ast
from llm import OpenAI
import numpy as np
from tools_context.index import DEFAULT_GIT_IGNORE_PATTERNS
import pathspec
from virtual_filesystem import FileSystem, VirtualFileSystem
from models import RangeInFile, Range, Traceback, TracebackFrame

gpt = OpenAI()

to_be_ignored_spec = pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, DEFAULT_GIT_IGNORE_PATTERNS)

def filter_traceback_frames(frames: List[TracebackFrame]) -> List[TracebackFrame]:
    """Filter out frames that are not relevant to the user's code."""
    return list(filter(lambda x: not to_be_ignored_spec.match_file(x.filepath), frames))

def fl1(tb: Traceback) -> TracebackFrame:
    """Find the most relevant frame in the traceback."""
    relevant = filter_traceback_frames(tb.frames)
    if len(relevant) == 0:
        return tb.frames[-1]
    return relevant[-1]

def parse_frame(frame: Dict) -> ast.AST:
    with open(frame['filepath'], "r") as f:
        code = f.read()
    
    return ast.parse(code)

def is_valid_context(node: ast.AST, lineno: int) -> bool:
    """Check if the node is a valid context for the line number."""
    # node.lineno - 1 because lineno starts at the body of the node, not the def or class line
    return (isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef)) and node.lineno - 1 <= int(lineno) <= node.end_lineno

def edit_context_ast(frame: Dict, replacement: Callable[[str], str]) -> ast.AST | None:
    """Get the surrounding context of a frame, and edit it, replacing the node in the AST and returning the updated version."""
    tree = parse_frame(frame)
    lineno = int(frame['lineno'])

    # Get the most specific function node containing the line
    for parent in ast.walk(tree):
        i = 0
        for child in ast.iter_child_nodes(parent):
            if is_valid_context(child, lineno):
                if len(list(filter(lambda x: is_valid_context(x, lineno), child.body))) > 0:
                    # More specific context can be found inthe body of this function
                    continue

                str_node = ast.unparse(child)
                new_node = ast.parse(replacement(str_node))
                parent.body[i] = new_node
                return tree
            i += 1

    return None

def find_most_specific_context(filecontents: str, lineno: int) -> ast.AST:
    # Get the most specific function node containing the line
    tree = ast.parse(filecontents)
    for parent in ast.walk(tree):
        i = 0
        for child in ast.iter_child_nodes(parent):
            if is_valid_context(child, lineno):
                if len(list(filter(lambda x: is_valid_context(x, lineno), child.body))) > 0:
                    # More specific context can be found inthe body of this function
                    continue
                
                return child
            i += 1
    # If we're here, it means that the code was top-level
    startline = lineno - 5
    endline = lineno + 5
    tree.body = list(filter(lambda node: startline <= node.lineno <= endline, tree.body))
    return tree

def find_code_in_range(filecontents: str, start: int, end: int) -> str:
    """Find the code in the given range in the file."""
    # TODO: This is the dumb version, want to later use AST to make sure we don't cut things off in the middle of a function/class
    lines = filecontents.splitlines()
    
    return "\n".join(lines[start - 1:end])

def indices_of_top_k(arr: List[float], k: int) -> List[int]:
    """Return the indices of the top k elements in the array."""
    return sorted(range(len(arr)), key=lambda i: arr[i])[-k:]

def fl2(tb: Traceback, query: str, filesystem: FileSystem=VirtualFileSystem({}), n: int = 4) -> List[TracebackFrame]:
    """Return the most relevant frames in the traceback."""
    filtered_frames = filter_traceback_frames(tb.frames)
    if len(filtered_frames) <= n:
        return filtered_frames

    # Find the most specific context for each frame, getting the code snippets
    surrounding_snippets = [
        filesystem.read_range_in_file(frame_to_code_range(frame, filesystem=filesystem))
        for frame in filtered_frames
    ]

    # Then, similarity search by the query to return top n frames
    embeddings = gpt.embed(surrounding_snippets + [query])
    similarities = [np.dot(embeddings[-1], x) for x in embeddings[:-1]]
    top_n = indices_of_top_k(similarities, n)

    return [filtered_frames[i] for i in top_n]

def get_ast_range(tree: ast.AST) -> Range:
    """Get the start and end line numbers of the AST node."""
    if isinstance(tree, ast.Module):
        return Range(
            startline=tree.body[0].lineno - 1,
            endline=tree.body[-1].end_lineno - 1,
            startcol=tree.body[0].col_offset,
            endcol=tree.body[-1].end_col_offset,
        )
    return Range(
        startline=tree.lineno - 1,
        endline=tree.end_lineno - 1,
        startcol=tree.col_offset,
        endcol=tree.end_col_offset,
    )

def frame_to_code_range(frame: TracebackFrame, filesystem: FileSystem=VirtualFileSystem({})) -> RangeInFile:
    """Get the CodeRange specified a traceback frame."""
    code = filesystem.read(frame.filepath)
    codelines = code.splitlines()
    for i in range(len(codelines) - 1):
        codelines[i] += "\n"

    ctx = find_most_specific_context(code, int(frame.lineno))
    code_range = get_ast_range(ctx)

    return RangeInFile(
        filepath=frame.filepath,
        range=code_range,
    )