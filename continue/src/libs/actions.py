from abc import abstractmethod
from typing import Generator, List

from pydantic import root_validator
from ..models.main import AbstractModel, Position, Range
from ..models.filesystem import FileSystem
from  .util.map_path import map_path
from .core import Action

class ReversibleAction(Action):
    reversible: bool = True

    @abstractmethod
    def reverse(self) -> Action:
        raise NotImplementedError
    
class SequentialAction(ReversibleAction):
    actions: List[Action]

    def reverse(self) -> Action:
        return SequentialAction([action.reverse() for action in reversed(self.actions)])
    
    def next_action(self) -> Generator["Action", None, None]:
        for action in self.actions:
            yield action

    def describe(self) -> str: # This will be used by LLM to generate summaries. This might be a good reason for creation of many Edit classes
        return " -> ".join([action.describe() for action in self.actions])

class FileSystemAction(ReversibleAction):
    filesystem: FileSystem
    @abstractmethod
    def with_mapped_paths(self, orig_root: str, copy_root: str) -> "FileSystemAction":
        raise NotImplementedError
    
class FileEdit(FileSystemAction):
    filepath: str
    range: Range
    replacement: str
    filesystem: FileSystem

    def apply(self):
        original_contents = self.filesystem.read(self.filepath)
        new_contents = self.filesystem.apply_edit_to_str(original_contents, self.range, self.replacement)
        self.filesystem.write(self.filepath, new_contents)
	
    def with_mapped_paths(self, orig_root: str, copy_root: str) -> FileSystemAction:
        return FileEdit(map_path(self.filepath, orig_root, copy_root), self.range, self.replacement)
    
    @staticmethod
    def from_deletion(filepath: str, start: Position, end: Position) -> "FileEdit":
        return FileEdit(filepath, Range(start, end), "")

    @staticmethod
    def from_insertion(filepath: str, position: Position, content: str) -> "FileEdit":
        return FileEdit(filepath, Range(position, position), content)
    
    def reverse(self) -> Action:
        # Reverse action determined right at creation, otherwise file contents might change
        replacement_lines = self.replacement.splitlines()
        replacement_d_lines = len(replacement_lines)
        replacement_d_chars = len(replacement_lines[-1])
        return FileEdit(
            self.filepath,
            Range(
                start=self.range.start,
                end=Position(
                    line=self.range.start + replacement_d_lines,
                    character=self.range.start.character + replacement_d_chars
                )
            ),
            self.filesystem.get_file(self.filepath).content[self.range.start:self.range.end]
        )

class AddFile(FileSystemAction):
    filepath: str
    content: str
	
    def with_mapped_paths(self, orig_root: str, copy_root: str) -> "FileSystemAction":
        return AddFile(self, map_path(self.filepath, orig_root, copy_root), self.content)
    
    def reverse(self) -> Action:
        return DeleteFile(self.filepath)

class DeleteFile(FileSystemAction):
    filepath: str
	
    def with_mapped_paths(self, orig_root: str, copy_root: str) -> "FileSystemAction":
        return DeleteFile(map_path(self.filepath, orig_root, copy_root))
    
    def reverse(self) -> Action:
        return AddFile(self.filepath, self.filesystem.read(self.filepath))

class RenameFile(FileSystemAction):
    filepath: str
    new_filepath: str

    def with_mapped_paths(self, orig_root: str, copy_root: str) -> "FileSystemAction":
        return RenameFile(map_path(self.filepath, orig_root, copy_root), map_path(self.new_filepath, orig_root, copy_root))
    
    def reverse(self) -> Action:
        return RenameFile(self.new_filepath, self.filepath)

class AddDirectory(FileSystemAction):
    path: str

    def with_mapped_paths(self, orig_root: str, copy_root: str) -> "FileSystemAction":
        return AddDirectory(map_path(self.path, orig_root, copy_root))
    
    def reverse(self) -> Action:
        return DeleteDirectory(self.path)

class DeleteDirectory(FileSystemAction):
    path: str
    
    def with_mapped_paths(self, orig_root: str, copy_root: str) -> "FileSystemAction":
        return DeleteDirectory(map_path(self.path, orig_root, copy_root))
    
    def reverse(self) -> Action:
        return AddDirectory(self.path)