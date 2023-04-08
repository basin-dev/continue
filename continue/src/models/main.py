from abc import ABC, abstractmethod
import os
from typing import Dict, Generator, List
from pydantic import BaseModel, root_validator
import difflib
from ..libs.map_path import map_path
from functools import total_ordering

@total_ordering
class Position(BaseModel):
    line: int
    character: int

    def __hash__(self):
        return hash((self.line, self.character))

    def __eq__(self, other: "Position") -> bool:
        return self.line == other.line and self.character == other.character

    def __lt__(self, other: "Position") -> bool:
        if self.line < other.line:
            return True
        elif self.line == other.line:
            return self.character < other.character
        else:
            return False

    @staticmethod
    def from_index(string: str, index: int) -> "Position":
        """Convert index in string to line and character"""
        line = string.count("\n", 0, index)
        if line == 1:
            character = index
        else:
            character = index - string.rindex("\n", 0, index) - 1

        return Position(line, character)

class Range(BaseModel):
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
    
    @staticmethod
    def from_indices(string: str, start_index: int, end_index: int) -> "Range":
        return Range(
            start=Position.from_index(string, start_index),
            end=Position.from_index(string, end_index)
        )
    
    @staticmethod
    def from_shorthand(start_line: int, start_char: int, end_line: int, end_char: int) -> "Range":
        return Range(
            start=Position(
                line=start_line,
                character=start_char
            ),
            end=Position(
                line=end_line,
                character=end_char
            )
        )

class AbstractModel(ABC, BaseModel):
    @root_validator(pre=True)
    def check_is_subclass(cls, values):
        if not issubclass(cls, AbstractModel):
            raise TypeError("AbstractModel subclasses must be subclasses of AbstractModel")

class TracebackFrame(BaseModel):
    filepath: str
    lineno: int
    function: str
    code: str | None

    def __eq__(self, other):
        return self.filepath == other.filepath and self.lineno == other.lineno and self.function == other.function

class Traceback(BaseModel):
    frames: List[TracebackFrame]
    message: str
    error_type: str
    full_traceback: str | None

    @classmethod
    def from_tbutil_parsed_exc(cls, tbutil_parsed_exc):
        return cls(
            frames=[
                TracebackFrame(
                    filepath=frame["filepath"],
                    lineno=frame["lineno"],
                    function=frame["funcname"],
                    code=frame["source_line"],
                )
                for frame in tbutil_parsed_exc.frames
            ],
            message=tbutil_parsed_exc.exc_msg,
            error_type=tbutil_parsed_exc.exc_type,
            full_traceback=tbutil_parsed_exc.to_string(),
        )
    
class FileSystemEdit(BaseModel):
    @abstractmethod
    def next_edit(self) -> Generator["FileSystemEdit", None, None]:
        raise NotImplementedError

    @abstractmethod
    def with_mapped_paths(self, orig_root: str, copy_root: str) -> "FileSystemEdit":
        raise NotImplementedError		

    @abstractmethod
    def describe(self) -> str: # This will be used by LLM to generate summaries. This might be a good reason for creation of many Edit classes
        raise NotImplementedError

class AtomicFileSystemEdit(FileSystemEdit):
    def next_edit(self) -> Generator["FileSystemEdit", None, None]:
        yield self

class FileEdit(AtomicFileSystemEdit):
    filepath: str
    range: Range
    replacement: str
	
    def with_mapped_paths(self, orig_root: str, copy_root: str) -> "FileSystemEdit":
        return FileEdit(map_path(self.filepath, orig_root, copy_root), self.range, self.replacement)
    
    @staticmethod
    def from_deletion(filepath: str, start: Position, end: Position) -> "FileEdit":
        return FileEdit(filepath, Range(start, end), "")

    @staticmethod
    def from_insertion(filepath: str, position: Position, content: str) -> "FileEdit":
        return FileEdit(filepath, Range(position, position), content)

class AddFile(AtomicFileSystemEdit):
    filepath: str
    content: str
	
    def with_mapped_paths(self, orig_root: str, copy_root: str) -> "FileSystemEdit":
        return AddFile(self, map_path(self.filepath, orig_root, copy_root), self.content)
	

class DeleteFile(AtomicFileSystemEdit):
    filepath: str
	
    def with_mapped_paths(self, orig_root: str, copy_root: str) -> "FileSystemEdit":
        return DeleteFile(map_path(self.filepath, orig_root, copy_root))

class RenameFile(AtomicFileSystemEdit):
    filepath: str
    new_filepath: str

    def with_mapped_paths(self, orig_root: str, copy_root: str) -> "FileSystemEdit":
        return RenameFile(map_path(self.filepath, orig_root, copy_root), map_path(self.new_filepath, orig_root, copy_root))

class AddDirectory(AtomicFileSystemEdit):
    path: str

    def with_mapped_paths(self, orig_root: str, copy_root: str) -> "FileSystemEdit":
        return AddDirectory(map_path(self.path, orig_root, copy_root))

class DeleteDirectory(AtomicFileSystemEdit):
    path: str
    
    def with_mapped_paths(self, orig_root: str, copy_root: str) -> "FileSystemEdit":
        return DeleteDirectory(map_path(self.path, orig_root, copy_root))

class RenameDirectory(AtomicFileSystemEdit):
    path: str
    new_path: str

    def with_mapped_paths(self, orig_root: str, copy_root: str) -> "FileSystemEdit":
        return RenameDirectory(map_path(self.filepath, orig_root, copy_root), map_path(self.new_path, orig_root, copy_root))

# You now have the atomic edits, and any other class needs to provide a generator which emits only these
class DeleteDirectoryRecursive(FileSystemEdit):
    path: str
	
    def with_mapped_paths(self, orig_root: str, copy_root: str) -> "FileSystemEdit":
        return DeleteDirectoryRecursive(map_path(self.path, orig_root, copy_root))

    # The thing about this...you need access to a filesystem. And hard to think of what other high-level edits people might invent.
    # This might just be really unecessary
    def next_edit(self) -> Generator[FileSystemEdit, None, None]:
        yield DeleteDirectory(path=self.path)
        for child in os.listdir(self.path):
            child_path = os.path.join(self.path, child)
            if os.path.isdir(child_path):
                yield DeleteDirectoryRecursive(path=child_path)
            else:
                yield DeleteFile(filepath=child_path)

class SequentialFileSystemEdit(FileSystemEdit):
    edits: List[FileSystemEdit]
	
    def with_mapped_paths(self, orig_root: str, copy_root: str) -> "FileSystemEdit":
        return SequentialFileSystemEdit([
			edit.with_mapped_paths(orig_root, copy_root)
			for edit in self.edits
		])

    def next_edit(self) -> Generator[FileSystemEdit, None, None]:
        for edit in self.edits:
            yield from edit.next_edit()

class EditDiff(BaseModel):
    """A reversible edit that can be applied to a file."""
    forward: FileSystemEdit
    backward: FileSystemEdit