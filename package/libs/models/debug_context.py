# Mostly living here only to avoid circular imports.

from typing import List
from pydantic import BaseModel

from ..util import parse_traceback
from .main import RangeInFile, SerializedVirtualFileSystem, Traceback
from ..virtual_filesystem import FileSystem, VirtualFileSystem

class DebugContext(BaseModel):
    traceback: Traceback | None
    ranges_in_files: List[RangeInFile]
    filesystem: FileSystem
    description: str | None

    class Config:
        arbitrary_types_allowed = True

class SerializedDebugContext(BaseModel):
    traceback: str | None
    ranges_in_files: List[RangeInFile]
    filesystem: SerializedVirtualFileSystem
    description: str | None

    def deserialize(self):
        traceback = None
        try:
            traceback = parse_traceback(self.traceback)
        except Exception as e:
            print("Unable to parse traceback: ", self.traceback)
        return DebugContext(
            traceback=traceback,
            ranges_in_files=self.ranges_in_files,
            filesystem=VirtualFileSystem(self.filesystem),
            description=self.description
        )