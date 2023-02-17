from typing import Callable, Dict, List, Tuple
from boltons import tbutils
import ast
import importlib
from pydantic import BaseModel
from .llm import OpenAI
import numpy as np
from .tools_context.index import DEFAULT_GIT_IGNORE_PATTERNS
import pathspec
from .virtual_filesystem import FileSystem, VirtualFileSystem
from .models import RangeInFile, Range, Traceback, TracebackFrame, Position
import os

gpt = OpenAI()

to_be_ignored_spec = pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, DEFAULT_GIT_IGNORE_PATTERNS)

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

def fl_assert(tb: Traceback, filesystem: FileSystem=VirtualFileSystem({})) -> List[RangeInFile]:
    """Given a traceback which is only an assertion error, return the most likely locations of the bug."""
    if not tb.message.startswith("AssertionError"):
        return []
    
    range_in_file = frame_to_code_range(tb.frames[-1], filesystem=filesystem)
    code = filesystem.read_range_in_file(range_in_file)
    fn_tree = ast.parse(code)
    call_graph = create_call_graph(fn_tree, range_in_file, filesystem=filesystem)
    pass
    
class CallGraph(BaseModel):
    """A call graph of a function."""
    function_name: str
    function_range: RangeInFile
    calls: List['CallGraph']

# TODO: Note that you're not handling attribute calls. If call.func is ast.Attribute, then this will have a value of the class and .attr of the function name
# and you have to take this into account for the import resolution too

def create_call_graph(fn: ast.FunctionDef | ast.AsyncFunctionDef, fn_range: RangeInFile, filesystem: FileSystem=VirtualFileSystem({}), max_depth: int=3, max_nodes: int=8, depth: int=0, nodes: int=0):
    """Create a call graph of the function that the line is in."""
    if depth >= max_depth or nodes >= max_nodes or to_be_ignored_spec.match_file(fn_range.filepath):
        return None

    call_graph = CallGraph(function_name=fn.name, function_range=fn_range, calls=[])
    for node in ast.walk(fn):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            def_lineno, def_filepath = goto_definition()
            def_range = frame_to_code_range(TracebackFrame(filepath=def_filepath, lineno=def_lineno, function=node.func.id))

            sub_graph = create_call_graph(node.func.id, def_lineno, def_range, filesystem=filesystem,
                            depth=depth+1,
                            nodes=nodes + len(call_graph.calls)
                        )
            if sub_graph:
                call_graph.calls.append(sub_graph)

    return call_graph

def resolve_module(imported_from_path: str, module_name: str) -> str:
    pass

def goto_definition(fn_name: str, call_range: RangeInFile, filesystem: FileSystem=VirtualFileSystem({})) -> Tuple[int, str] | None:
    curr_file_tree = ast.parse(filesystem.read(call_range.filepath))

    def fn_def_criterion(node: ast.AST) -> bool:
        return isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef) and node.name == fn_name

    # Look in current file for definition
    if line_in_curr_file := find_last_node(curr_file_tree, fn_def_criterion):
        return line_in_curr_file, call_range.filepath
    
    # Look for and resolve import to find filepath of module with definition
    src_module_name = None
    for node in ast.walk(curr_file_tree):
        if isinstance(node, ast.Import):
            pass # Need to deal with ast.Attribute
        elif isinstance(node, ast.ImportFrom):
            if fn_name in list(map(lambda x: x.name, node.names)):
                src_module_name = node.module
                break
    
    # This is the main issue—also that you need to retrieve files from the client.
    module_spec = importlib.util.find_spec(src_module_name, package=call_range.filepath) # How do we guess whether this was the root script, or whether it was a module?
    # Maybe use the traceback to get the location of the main package
    # What if we changed our product to a tag that could be placed in the code to debug it?
    # In python, just a with statement, or maybe an alternative to python3 CLI
    if module_spec is None:
        return None
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)

    # Get the path to the module file
    module_path = module.__file__
    module_contents = filesystem.read(module_path)
    module_tree = ast.parse(module_contents)
    
    if line_in_module_file := find_last_node(module_contents, fn_def_criterion):
        return line_in_module_file, module_path
    
    return None

def find_first_node(tree: ast.AST, criterion: Callable[[ast.AST], bool]) -> ast.AST | None:
    for node in ast.walk(tree):
        if criterion(node):
            return node
    return None

def find_last_node(tree: ast.AST, criterion: Callable[[ast.AST], bool]) -> ast.AST | None:
    result = None
    for node in ast.walk(tree):
        if criterion(node):
            result = node
    return result

def find_fn_def_range(filepath: str, fn_name: str, filesystem: FileSystem=VirtualFileSystem({})) -> RangeInFile:
    tree = ast.parse(filesystem.read(filepath))
    
    def fn_def_criterion(node: ast.AST) -> bool:
        return isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef) and node.name == fn_name
    
    node = find_last_node(tree, fn_def_criterion)
    
    return RangeInFile(
        filepath=filepath,
        range=get_ast_range(node)
    )

def prune_call_graph(call_graph: CallGraph, filesystem: FileSystem=VirtualFileSystem({})) -> CallGraph:
    """A number of pruning strategies are used here:
        - Ignore files that are not ours
        - Don't enter a function that's already been seen
        - If given a constraint on size, take the shallowest nodes
    """
    pass

def fl2(tb: Traceback, query: str, filesystem: FileSystem=VirtualFileSystem({}), n: int = 4) -> List[TracebackFrame]:
    """Return the most relevant frames in the traceback."""
    filtered_frames = filter_ignored_traceback_frames(tb.frames)
    filtered_frames = filter_test_traceback_frames(filtered_frames)
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
            start=Position(
                line=tree.body[0].lineno - 1,
                character=tree.body[0].col_offset,
            ),
            end=Position(  
                line=tree.body[-1].end_lineno - 1,
                character=tree.body[-1].end_col_offset,
            ),
        )
    return Range(
        start=Position(
            line=tree.lineno - 1,
            character=tree.col_offset,
        ),
        end=Position(
            line=tree.end_lineno - 1,
            character=tree.end_col_offset,
        ),
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