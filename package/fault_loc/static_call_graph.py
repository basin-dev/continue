import importlib
from typing import List, Tuple, Union
import pathspec
from package.fault_loc.utils import find_last_node, frame_to_code_range, get_ast_range, find_all_nodes, ast_in_range
from package.libs.models.main import CallGraph, Position, RangeInFile, TracebackFrame, Range
from package.libs.virtual_filesystem import FileSystem, RealFileSystem, VirtualFileSystem
from package.libs.filesystem.main import DEFAULT_GIT_IGNORE_PATTERNS, upward_search_in_filetree
import ast
import importlib.machinery as im
import importlib.util

to_be_ignored_spec = pathspec.PathSpec.from_lines(
    pathspec.patterns.GitWildMatchPattern, DEFAULT_GIT_IGNORE_PATTERNS)


def create_call_graph(fn_name: str, fn_range: RangeInFile, filesystem: FileSystem = VirtualFileSystem({}), max_depth: int = 3, max_nodes: int = 8, depth: int = 0, nodes: int = 0):
    """Create a call graph of the function that the line is in."""
    if depth >= max_depth or nodes >= max_nodes or to_be_ignored_spec.match_file(fn_range.filepath):
        return None

    call_graph = CallGraph(function_name=fn_name,
                           function_range=fn_range, calls=[])
    for node in ast.walk(ast.parse(filesystem.read(fn_range.filepath))):
        if ast_in_range(node, fn_range.range) and isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            definition_ranges = goto_definitions(
                node.func.id, fn_range.filepath, filesystem=filesystem)
            if len(definition_ranges) == 0:
                continue
            sub_graph = create_call_graph(node.func.id, definition_ranges[-1], filesystem=filesystem,
                                          depth=depth+1,
                                          nodes=nodes + len(call_graph.calls)
                                          )
            if sub_graph:
                call_graph.calls.append(sub_graph)

    return call_graph


def find_module_in_path(path: str, module: str) -> Union[str, None]:
    """Check if a path has a module."""
    spec = im.FileFinder(path, (importlib.util.LazyLoader.factory(
        im.SourceFileLoader), im.SOURCE_SUFFIXES)).find_spec(module)
    if spec is None:
        return None
    return spec.origin


def get_fn_def_in_file(filepath: str, fn_name: str) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    # TODO: Should use fn_signature instead of fn_name to be more accurate
    def fn_def_criterion(node: ast.AST) -> bool:
        return (isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef)) and node.name == fn_name

    with open(filepath, "r") as f:
        tree = ast.parse(f.read())

    return find_last_node(tree, fn_def_criterion)


def get_imports_in_file(filepath: str, imported_name: str) -> List[ast.Import | ast.ImportFrom]:
    def import_criterion(node: ast.AST) -> bool:
        return isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom) and imported_name in list(map(lambda x: x.name, node.names))

    with open(filepath, "r") as f:
        tree = ast.parse(f.read())

    return find_all_nodes(tree, import_criterion)


def resolve_python_module(imported_from_path: str, module: str, name: str) -> List[RangeInFile]:
    """Resolve a module name to a filepath."""
    packages = module.split('.')
    candidate_roots = upward_search_in_filetree(
        packages[0], imported_from_path) + upward_search_in_filetree(packages[0] + ".py", imported_from_path)
    valid_paths = set()
    for candidate_root in candidate_roots:
        sub_path = candidate_root
        no_exit = True
        for package in packages[1:]:
            sub_path = find_module_in_path(sub_path, package)
            if sub_path is None:
                no_exit = False
                break
        if no_exit:
            valid_paths.add(sub_path)

    range_in_files = []
    for filepath in valid_paths:
        if fn_def := get_fn_def_in_file(filepath, name):
            range_in_files.append(RangeInFile(
                filepath=filepath,
                range=get_ast_range(fn_def)
            ))

    return range_in_files


def goto_definitions(fn_name: str, call_filepath: str, filesystem: FileSystem = VirtualFileSystem({})) -> List[RangeInFile]:
    # Look in current file for definition
    if fn_def := get_fn_def_in_file(call_filepath, fn_name):
        return [RangeInFile(
            filepath=call_filepath,
            range=get_ast_range(fn_def)
        )]

    # Look for and resolve import to find filepath of module with definition
    resolved_ranges = []
    imports = get_imports_in_file(call_filepath, fn_name)
    for imp in imports:
        if isinstance(imp, ast.Import):
            pass
        elif isinstance(imp, ast.ImportFrom):
            if fn_name in list(map(lambda x: x.name, imp.names)):
                module = imp.module
                resolved_ranges += resolve_python_module(
                    call_filepath, module, fn_name)

    return resolved_ranges
