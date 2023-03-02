import ast
from ..libs.virtual_filesystem import FileSystem, VirtualFileSystem
from ..libs.models.main import RangeInFile, Range, Position, Traceback, TracebackFrame
from typing import Callable, List
import os.path

def find_fn_def_range(filepath: str, fn_name: str, filesystem: FileSystem=VirtualFileSystem({})) -> RangeInFile:
    tree = ast.parse(filesystem.read(filepath))
    
    def fn_def_criterion(node: ast.AST) -> bool:
        return isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef) and node.name == fn_name
    
    node = find_last_node(tree, fn_def_criterion)
    
    return RangeInFile(
        filepath=filepath,
        range=get_ast_range(node)
    )

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

def find_all_nodes(tree: ast.AST, criterion: Callable[[ast.AST], bool]) -> List[ast.AST]:
    result = []
    for node in ast.walk(tree):
        if criterion(node):
            result.append(node)
    return result

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

def ast_in_range(tree: ast.AST, range: Range) -> bool:
    """Check if the AST node is within the range."""
    try:
        ast_range = get_ast_range(tree)
    except:
        # Some types of AST dont' have lineno and end_lineno
        return False
    return range.start <= ast_range.start and ast_range.end <= range.end

def is_valid_context(node: ast.AST, lineno: int) -> bool:
    """Check if the node is a valid context for the line number."""
    # node.lineno - 1 because lineno starts at the body of the node, not the def or class line
    return (isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef)) and node.lineno - 1 <= int(lineno) <= node.end_lineno

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

def is_test_file(filepath: str) -> bool:
    basename = os.path.basename(filepath)
    return basename.startswith("test_") or basename.endswith("_test.py")

def shorten_traceback(tb: Traceback) -> Traceback:
    """If RecursionError, cut off the traceback."""
    if tb.error_type.startswith("RecursionError"):
        # Figure out the repeating pattern
        pattern = []
        for frame in reversed(tb.frames):
            if frame == tb.frames[0]:
                break
            pattern.append(frame)

        # Remove the repeating pattern
        while all([tb.frames[len(tb.frames) - 1 - i] == pattern[i] for i in range(len(pattern))]):
            tb.frames = tb.frames[:-len(pattern)]

        # Add back a single instance of the pattern
        tb.frames += reversed(pattern)
    
    return tb
    