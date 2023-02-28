# Mostly living here only to avoid circular imports.

from typing import List
from pydantic import BaseModel

from ..util import parse_traceback
from .main import RangeInFile, SerializedVirtualFileSystem, Traceback
from ..virtual_filesystem import FileSystem, VirtualFileSystem

class DebugContext(BaseModel):
    traceback: Traceback
    ranges_in_files: List[RangeInFile]
    filesystem: FileSystem
    description: str

    class Config:
        arbitrary_types_allowed = True

class SerializedDebugContext(BaseModel):
    traceback: str
    ranges_in_files: List[RangeInFile]
    filesystem: SerializedVirtualFileSystem
    description: str

    def deserialize(self):
        return DebugContext(
            traceback=parse_traceback(self.traceback),
            ranges_in_files=self.ranges_in_files,
            filesystem=VirtualFileSystem(self.filesystem),
            description=self.description
        )