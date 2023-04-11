from abc import ABC, abstractmethod
from typing import Dict, List, Tuple
import os
from ..models.main import Range, AbstractModel
from pydantic import BaseModel

class RangeInFile(BaseModel):
    filepath: str
    range: Range

    def __hash__(self):
        return hash((self.filepath, self.range))
    
    @staticmethod
    def from_entire_file(filepath: str, filesystem: "FileSystem") -> "RangeInFile":
        lines = filesystem.readlines(filepath)
        return RangeInFile(
            filepath=filepath,
            range=Range.from_shorthand(0, 0, len(lines) - 1, len(lines[-1]) - 1)
        )

class FileSystem(AbstractModel):
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
    
    # Probably none of these should be exported, should all be used only through apply_edit
    @abstractmethod
    def rename_file(self, filepath: str, new_filepath: str):
        raise NotImplementedError
    
    @abstractmethod
    def rename_directory(self, path: str, new_path: str):
        raise NotImplementedError
    
    @abstractmethod
    def delete_file(self, filepath: str):
        raise NotImplementedError
    
    @abstractmethod
    def delete_directory(self, path: str):
        raise NotImplementedError
    
    @abstractmethod
    def add_directory(self, path: str):
        raise NotImplementedError
    
    @classmethod
    def read_range_in_str(self, s: str, r: Range) -> str:
        lines = s.splitlines()[r.start.line:r.end.line + 1]
        lines[0] = lines[0][r.start.character:]
        lines[-1] = lines[-1][:r.end.character + 1]
        return "\n".join(lines)
    
    @classmethod
    def apply_edit_to_str(self, s: str, range: Range, replacement: str) -> str:
        lines = s.splitlines()
        before_lines = lines[:range.start.line]
        after_lines = lines[range.end.line + 1:]
        between_str = lines[range.start.line][:range.start.character] + replacement + lines[range.end.line][range.end.character + 1:]
        
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
    
    def rename_file(self, filepath: str, new_filepath: str):
        os.rename(filepath, new_filepath)
    
    def rename_directory(self, path: str, new_path: str):
        os.rename(path, new_path)
    
    def delete_file(self, filepath: str):
        os.remove(filepath)
    
    def delete_directory(self, path: str):
        raise NotImplementedError
    
    def add_directory(self, path: str):
        os.makedirs(path)
    
class VirtualFileSystem(FileSystem):
    """A simulated filesystem from a mapping of filepath to file contents."""
    files: Dict[str, str]
    def __init__(self, files: Dict[str, str]):
        self.files = files
    
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
    
    def rename_file(self, filepath: str, new_filepath: str):
        self.files[new_filepath] = self.files[filepath]
        del self.files[filepath]
    
    def rename_directory(self, path: str, new_path: str):
        for filepath in self.files:
            if filepath.startswith(path):
                new_filepath = new_path + filepath[len(path):]
                self.files[new_filepath] = self.files[filepath]
                del self.files[filepath]
    
    def delete_file(self, filepath: str):
        del self.files[filepath]
    
    def delete_directory(self, path: str):
        raise NotImplementedError
    
    def add_directory(self, path: str):
        pass # For reasons as seen here and in delete_directory, a Dict[str, str] might not be the best represntation. Could just preprocess to something better upon __init__
    
# A big todo in this file is to have uniform errors thrown by any FileSystem subclass.