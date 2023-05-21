from abc import ABC, abstractmethod
from pydantic import BaseModel, Extra
from typer import Typer
import json
import importlib
from typing import Callable, Dict, List, Union
import pathspec
import ast
import importlib.machinery as im
import importlib.util
import os

app = Typer()

# region copied code


class StrictBaseModel(BaseModel):
    class Config:
        extra = Extra.forbid


class Position(StrictBaseModel):
    line: int
    character: int

    def __hash__(self):
        return hash((self.line, self.character))

    def __le__(self, other: "Position") -> bool:
        return self < other or self == other

    def __ge__(self, other: "Position") -> bool:
        return self > other or self == other

    def __eq__(self, other: "Position") -> bool:
        return self.line == other.line and self.character == other.character

    def __lt__(self, other: "Position") -> bool:
        if self.line < other.line:
            return True
        elif self.line == other.line:
            return self.character < other.character
        else:
            return False

    def __gt__(self, other: "Position") -> bool:
        if self.line > other.line:
            return True
        elif self.line == other.line:
            return self.character > other.character
        else:
            return False


class Range(StrictBaseModel):
    """A range in a file. 0-indexed."""
    start: Position
    end: Position

    def __hash__(self):
        return hash((self.start, self.end))

    def union(self, other: "Range") -> "Range":
        return Range(
            start=min(self.start, other.start),
            end=max(self.end, other.end),
        )

    def overlaps_with(self, other: "Range") -> bool:
        return not (self.end < other.start or self.start > other.end)


class TracebackFrame(StrictBaseModel):
    filepath: str
    lineno: int
    function: str
    code: Union[str, None]

    def __eq__(self, other):
        return self.filepath == other.filepath and self.lineno == other.lineno and self.function == other.function


class RangeInFile(StrictBaseModel):
    filepath: str
    range: Range

    def __hash__(self):
        return hash((self.filepath, self.range))


class CallGraph(StrictBaseModel):
    """A call graph of a function."""
    function_name: str
    function_range: RangeInFile
    calls: List['CallGraph']

    def get_all_ranges(self) -> List[RangeInFile]:
        return list(set([self.function_range] + sum([call.get_all_ranges() for call in self.calls], [])))

    def pretty_print(self) -> str:
        return self.function_name + "\n  " + "\n  ".join(list(map(lambda call: call.pretty_print(), self.calls)))


def find_last_node(tree: ast.AST, criterion: Callable[[ast.AST], bool]) -> Union[ast.AST, None]:
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


def upward_search_in_filetree(search_for: str, start_path: str = ".") -> List[str]:
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
]


class FileEdit(StrictBaseModel):
    filepath: str
    range: Range
    replacement: str


class FileSystem(ABC):
    """An abstract filesystem that can read/write from a set of files."""
    @abstractmethod
    def read(self, path) -> str:
        raise NotImplementedError

    @abstractmethod
    def readlines(self, path) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def write(self, path, content):
        raise NotImplementedError

    @abstractmethod
    def exists(self, path) -> bool:
        raise NotImplementedError

    @abstractmethod
    def read_range_in_file(self, r: RangeInFile) -> str:
        raise NotImplementedError

    @abstractmethod
    def apply_file_edit(self, edit: FileEdit):
        raise NotImplementedError

    @classmethod
    def read_range_in_str(self, s: str, r: Range) -> str:
        lines = s.splitlines()[r.start.line:r.end.line + 1]
        lines[0] = lines[0][r.start.character:]
        lines[-1] = lines[-1][:r.end.character + 1]
        return "\n".join(lines)

    @classmethod
    def apply_edit_to_str(self, s: str, edit: FileEdit) -> str:
        lines = s.splitlines()
        before_lines = lines[:edit.range.start.line]
        after_lines = lines[edit.range.end.line + 1:]
        between_str = lines[edit.range.start.line][:edit.range.start.character] + \
            edit.replacement + \
            lines[edit.range.end.line][edit.range.end.character + 1:]

        lines = before_lines + between_str.splitlines() + after_lines
        return "\n".join(lines)


SerializedVirtualFileSystem = Dict[str, str]


class RealFileSystem(FileSystem):
    """A filesystem that reads/writes from the actual filesystem."""

    def read(self, path) -> str:
        with open(path, "r") as f:
            return f.read()

    def readlines(self, path) -> List[str]:
        with open(path, "r") as f:
            return f.readlines()

    def write(self, path, content):
        with open(path, "w") as f:
            f.write(content)

    def exists(self, path) -> bool:
        return os.path.exists(path)

    def read_range_in_file(self, r: RangeInFile) -> str:
        return FileSystem.read_range_in_str(self.read(r.filepath), r.range)

    def apply_file_edit(self, edit: FileEdit):
        old_content = self.read(edit.filepath)
        new_content = FileSystem.apply_edit_to_str(old_content, edit)
        self.write(edit.filepath, new_content)


class VirtualFileSystem(FileSystem):
    """A simulated filesystem from a mapping of filepath to file contents."""
    files: SerializedVirtualFileSystem

    def __init__(self, files: SerializedVirtualFileSystem):
        self.files = files

    @classmethod
    def from_serialized(cls, serialized: SerializedVirtualFileSystem):
        return cls(serialized)

    def serialize(self) -> SerializedVirtualFileSystem:
        return self.files.copy()

    def read(self, path) -> str:
        return self.files[path]

    def readlines(self, path) -> List[str]:
        return self.files[path].splitlines()

    def write(self, path, content):
        self.files[path] = content

    def exists(self, path) -> bool:
        return path in self.files

    def read_range_in_file(self, r: RangeInFile) -> str:
        return FileSystem.read_range_in_str(self.read(r.filepath), r.range)

    def apply_file_edit(self, edit: FileEdit):
        old_content = self.read(edit.filepath)
        new_content = FileSystem.apply_edit_to_str(old_content, edit)
        self.write(edit.filepath, new_content)


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
    tree.body = list(filter(lambda node: startline <=
                     node.lineno <= endline, tree.body))
    return tree


def frame_to_code_range(frame: TracebackFrame, filesystem: FileSystem = VirtualFileSystem({})) -> RangeInFile:
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

# endregion

# region copied, but should be here code


to_be_ignored_spec = pathspec.PathSpec.from_lines(
    pathspec.patterns.GitWildMatchPattern, DEFAULT_GIT_IGNORE_PATTERNS)


def better_creat_call_graph(tb_frame: TracebackFrame, filesystem: FileSystem = VirtualFileSystem({}), max_depth: int = 3, max_nodes: int = 8, depth: int = 0, nodes: int = 0):
    fn_range = frame_to_code_range(tb_frame, filesystem=filesystem)
    return create_call_graph(tb_frame.function, fn_range, filesystem=filesystem, max_depth=max_depth, max_nodes=max_nodes, depth=depth, nodes=nodes)


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


def get_fn_def_in_file(filepath: str, fn_name: str) -> Union[ast.FunctionDef, ast.AsyncFunctionDef,  None]:
    # TODO: Should use fn_signature instead of fn_name to be more accurate
    def fn_def_criterion(node: ast.AST) -> bool:
        return (isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef)) and node.name == fn_name

    with open(filepath, "r") as f:
        tree = ast.parse(f.read())

    return find_last_node(tree, fn_def_criterion)


def get_imports_in_file(filepath: str, imported_name: str) -> List[ast.Import | ast.ImportFrom]:
    def import_criterion(node: ast.AST) -> bool:
        if isinstance(node, ast.Import):
            return True  # TODO
        elif isinstance(node, ast.ImportFrom):
            names = list(map(lambda x: x.name, node.names))
            return imported_name in names or '*' in names
        else:
            return False

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
            module = imp.module
            resolved_ranges += resolve_python_module(
                call_filepath, module, fn_name)

    return resolved_ranges

# endregion


@app.command()
def build_call_graph(filepath: str, lineno: int, function: str):
    try:
        tb_frame = TracebackFrame(
            filepath=filepath,
            lineno=lineno,
            function=function,
        )
        call_graph = better_creat_call_graph(tb_frame, RealFileSystem())
        print({"value": list(map(lambda x: x.dict(), call_graph.get_all_ranges()))})
    except Exception as e:
        print({"error": str(e)})


if __name__ == "__main__":
    app()
