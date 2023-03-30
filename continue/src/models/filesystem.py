from abc import ABC, abstractmethod
from typing import Dict, List, Tuple
import os
from ..models.main import EditDiff, Position, Range, FileEdit, FileSystemEdit, AddFile, DeleteFile, RenameFile, AddDirectory, RenameDirectory, DeleteDirectory, SequentialFileSystemEdit
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
    
    @abstractmethod
    def apply_file_edit(self, edit: FileEdit):
        raise NotImplementedError
    
    @abstractmethod
    def apply_edit(self, edit: FileSystemEdit) -> EditDiff:
        """Apply edit to filesystem, calculate the reverse edit, and return and EditDiff"""
        raise NotImplementedError
    
    @classmethod
    def read_range_in_str(self, s: str, r: Range) -> str:
        lines = s.splitlines()[r.start.line:r.end.line + 1]
        lines[0] = lines[0][r.start.character:]
        lines[-1] = lines[-1][:r.end.character + 1]
        return "\n".join(lines)
    
    @classmethod
    def apply_edit_to_str(self, s: str, edit: FileEdit) -> Tuple[str, EditDiff]:
        original = self.read_range_in_str(s, edit.range)

        lines = s.splitlines()
        before_lines = lines[:edit.range.start.line]
        after_lines = lines[edit.range.end.line + 1:]
        between_str = lines[edit.range.start.line][:edit.range.start.character] + edit.replacement + lines[edit.range.end.line][edit.range.end.character + 1:]

        new_range = Range(
            start=edit.range.start,
            end=Position(
                line=edit.range.start.line + len(edit.replacement.splitlines()) - 1,
                character=edit.range.start.character + len(edit.replacement.splitlines()[-1])
            )
        )
        
        lines = before_lines + between_str.splitlines() + after_lines
        return "\n".join(lines), EditDiff(
            forward=edit,
            backward=FileEdit(
                filepath=edit.filepath,
                range=new_range,
                replacement=original
            )
        )
    
    @classmethod
    def reverse_edit_on_str(self, s: str, diff: EditDiff) -> str:
        lines = s.splitlines()

        replacement_lines = diff.replacement.splitlines()
        replacement_d_lines = len(replacement_lines)
        replacement_d_chars = len(replacement_lines[-1])
        replacement_range = Range(
            start=diff.edit.range.start,
            end=Position(
                line=diff.edit.range.start + replacement_d_lines,
                character=diff.edit.range.start.character + replacement_d_chars
            )
        )

        before_lines = lines[:replacement_range.start.line]
        after_lines = lines[replacement_range.end.line + 1:]
        between_str = lines[replacement_range.start.line][:replacement_range.start.character] + diff.original + lines[replacement_range.end.line][replacement_range.end.character + 1:]
        
        lines = before_lines + between_str.splitlines() + after_lines
        return "\n".join(lines)
    
    @classmethod
    def apply_edit(self, edit: FileSystemEdit) -> EditDiff:
        backward = None
        if isinstance(edit, FileEdit):
            backward = self.apply_file_edit(edit)
        elif isinstance(edit, AddFile):
            self.write(edit.filepath, edit.content)
            backward = DeleteFile(edit.filepath)
        elif isinstance(edit, DeleteFile):
            contents = self.read(edit.filepath)
            backward = AddFile(edit.filepath, contents)
            self.delete_file(edit.filepath)
        elif isinstance(edit, RenameFile):
            self.rename_file(edit.filepath, edit.new_filepath)
            backward = RenameFile(filepath=edit.new_filepath, new_filepath=edit.filepath)
        elif isinstance(edit, AddDirectory):
            self.add_directory(edit.path)
            backward = DeleteDirectory(edit.path)
        elif isinstance(edit, DeleteDirectory):
            # This isn't atomic!
            backward_edits = []
            for root, dirs, files in os.walk(edit.path, topdown=False):
                for f in files:
                    path = os.path.join(root, f)
                    backward_edits.append(self.apply_edit(DeleteFile(path)))
                for d in dirs:
                    path = os.path.join(root, d)
                    backward_edits.append(self.apply_edit(DeleteDirectory(path)))

            backward_edits.append(self.apply_edit(DeleteDirectory(edit.path)))
            backward_edits.reverse()
            backward = SequentialFileSystemEdit(edits=backward_edits)
        elif isinstance(edit, RenameDirectory):
            self.rename_directory(edit.path, edit.new_path)
            backward = RenameDirectory(path=edit.new_path, new_path=edit.path)
        elif isinstance(edit, FileSystemEdit):
            backward_edits = []
            for edit in edit.next_edit():
                backward_edits.append(self.apply_edit(edit))
            backward_edits.reverse()
            backward = SequentialFileSystemEdit(edits=backward_edits)
        else:
            raise TypeError("Unknown FileSystemEdit type: " + str(type(edit)))

        return EditDiff(
            forward=edit,
            backward=backward
        )

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
    
    @abstractmethod
    def delete_directory(self, path: str):
        raise NotImplementedError
    
    def add_directory(self, path: str):
        os.makedirs(path)
    
    def apply_file_edit(self, edit: FileEdit) -> EditDiff:
        old_content = self.read(edit.filepath)
        new_content, diff = FileSystem.apply_edit_to_str(old_content, edit)
        self.write(edit.filepath, new_content)
        return diff
    
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
    
    @abstractmethod
    def delete_directory(self, path: str):
        raise NotImplementedError
    
    def add_directory(self, path: str):
        pass # For reasons as seen here and in delete_directory, a Dict[str, str] might not be the best represntation. Could just preprocess to something better upon __init__
    
    def apply_file_edit(self, edit: FileEdit) -> EditDiff:
        old_content = self.read(edit.filepath)
        new_content, original = FileSystem.apply_edit_to_str(old_content, edit)
        self.write(edit.filepath, new_content)
        return EditDiff(
            edit=edit,
            original=original
        )
    
# A big todo in this file is to have uniform errors thrown by any FileSystem subclass.