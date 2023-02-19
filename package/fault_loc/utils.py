import ast
from ..virtual_filesystem import FileSystem, VirtualFileSystem
from ..models import RangeInFile, Range, Position
from typing import Callable

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