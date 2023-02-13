from abc import ABC, abstractmethod
from typing import Dict, List
import os
from models import SerializedVirtualFileSystem, RangeInFile, Range, FileEdit

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
        between_str = lines[edit.range.start.line][:edit.range.start.character] + edit.replacement + lines[edit.range.end.line][edit.range.end.character + 1:]
        
        lines = before_lines + between_str.splitlines() + after_lines
        return "\n".join(lines)

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