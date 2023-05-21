from typing import Callable, Dict, List, Tuple, Union
from boltons import tbutils
import ast
from pydantic import BaseModel
from ..libs.language_models.llm import OpenAI
import numpy as np
from ..libs.filesystem.main import DEFAULT_GIT_IGNORE_PATTERNS
import pathspec
from ..libs.virtual_filesystem import FileSystem, VirtualFileSystem
from ..libs.models.main import RangeInFile, Range, Traceback, TracebackFrame, Position, CallGraph
import os
from .dyn_call_graph import prune_call_graph
from .utils import frame_to_code_range, is_valid_context, shorten_traceback
from .static_call_graph import create_call_graph

gpt = OpenAI()

to_be_ignored_spec = pathspec.PathSpec.from_lines(
    pathspec.patterns.GitWildMatchPattern, DEFAULT_GIT_IGNORE_PATTERNS)


def filter_ignored_traceback_frames(frames: List[TracebackFrame]) -> List[TracebackFrame]:
    """Filter out frames that are not relevant to the user's code."""
    return list(filter(lambda x: not to_be_ignored_spec.match_file(x.filepath), frames))


def filter_test_traceback_frames(frames: List[TracebackFrame]) -> List[TracebackFrame]:
    """Filter out frames that are test files."""
    not_test = []
    for frame in frames:
        basename = os.path.basename(frame.filepath)
        if basename.endswith("_test.py") or basename.startswith("test_"):
            continue
        not_test.append(frame)

    return not_test


def fl1(tb: Traceback) -> TracebackFrame:
    """Find the most relevant frame in the traceback."""
    relevant = filter_ignored_traceback_frames(tb.frames)
    if len(relevant) == 0:
        return tb.frames[-1]
    return relevant[-1]


def parse_frame(frame: Dict) -> ast.AST:
    with open(frame['filepath'], "r") as f:
        code = f.read()

    return ast.parse(code)


def edit_context_ast(frame: Dict, replacement: Callable[[str], str]) -> Union[ast.AST, None]:
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


def find_code_in_range(filecontents: str, start: int, end: int) -> str:
    """Find the code in the given range in the file."""
    # TODO: This is the dumb version, want to later use AST to make sure we don't cut things off in the middle of a function/class
    lines = filecontents.splitlines()

    return "\n".join(lines[start - 1:end])


def indices_of_top_k(arr: List[float], k: int) -> List[int]:
    """Return the indices of the top k elements in the array."""
    return sorted(range(len(arr)), key=lambda i: arr[i])[-k:]


def fl_call_graph(tb: Traceback, filesystem: FileSystem = VirtualFileSystem({})) -> List[RangeInFile]:
    """Given a traceback which is only one line, return the most likely locations of the bug by generating a call graph."""
    range_in_file = frame_to_code_range(tb.frames[-1], filesystem=filesystem)
    call_graph = create_call_graph(
        tb.frames[-1].function, range_in_file, filesystem=filesystem)
    call_graph = prune_call_graph(call_graph)
    return call_graph.get_all_ranges()


def fl2(tb: Traceback, query: str, filesystem: FileSystem = VirtualFileSystem({}), n: int = 4) -> List[RangeInFile]:
    """Return the most relevant frames in the traceback."""
    if query is None or query == "":
        query = tb.message

    frames = shorten_traceback(tb).frames
    if len(tb.frames) == 1 and tb.error_type.startswith("AssertionError"):
        return fl_call_graph(tb, filesystem=filesystem)

    filtered_frames = filter_ignored_traceback_frames(frames)
    filtered_frames = filter_test_traceback_frames(filtered_frames)
    filtered_ranges = [frame_to_code_range(
        frame, filesystem=filesystem) for frame in filtered_frames]
    if len(filtered_frames) <= n:
        return filtered_ranges

    # Find the most specific context for each frame, getting the code snippets
    surrounding_snippets = [
        filesystem.read_range_in_file(filtered_range)
        for filtered_range in filtered_ranges
    ]

    # Then, similarity search by the query to return top n frames
    embeddings = gpt.embed(surrounding_snippets + [query])
    similarities = [np.dot(embeddings[-1], x) for x in embeddings[:-1]]
    top_n = indices_of_top_k(similarities, n)

    return [filtered_ranges[i] for i in top_n]
