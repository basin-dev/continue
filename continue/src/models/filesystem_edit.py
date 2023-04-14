from abc import abstractmethod
from typing import Generator, List
from pydantic import BaseModel
from .main import Position, Range
from ..libs.util.map_path import map_path


class FileSystemEdit(BaseModel):
    @abstractmethod
    def next_edit(self) -> Generator["FileSystemEdit", None, None]:
        raise NotImplementedError

    @abstractmethod
    def with_mapped_paths(self, orig_root: str, copy_root: str) -> "FileSystemEdit":
        raise NotImplementedError

    @abstractmethod
    def describe(self) -> str:  # This will be used by LLM to generate summaries. This might be a good reason for creation of many Edit classes
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
