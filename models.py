from typing import Dict, List
from pydantic import BaseModel, validator
import os
from enum import Enum

class CustomStringModel(BaseModel):
    __root__: str

    def __hash__(self):
        return hash(self.__root__)
    
    def __eq__(self, other):
        return self.__root__ == other
    
class CustomDictModel(BaseModel):
    __root__: Dict

    def __getitem__(self, key):
        return self.__root__[key]

# class AbsoluteFilePath(CustomStringModel):
#     __root__: str

    @validator("__root__")
    def validate_path(cls, v):
        if not os.path.isabs(v):
            raise ValueError("Path must be absolute")
        return v

class Position(BaseModel):
    line: int
    character: int

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

class Range(BaseModel):
    """A range in a file. 0-indexed."""
    start: Position
    end: Position

    def union(self, other: "Range") -> "Range":
        return Range(
            start=min(self.start, other.start),
            end=max(self.end, other.end),
        )

    def overlaps_with(self, other: "Range") -> bool:
        return not (self.end < other.start or self.start > other.end)

class RangeInFile(BaseModel):
    filepath: str
    range: Range

# class SerializedVirtualFileSystem(CustomDictModel):
    # __root__: Dict[AbsoluteFilePath, str]

SerializedVirtualFileSystem = Dict[str, str]

class TracebackFrame(BaseModel):
    filepath: str
    lineno: int
    function: str
    code: str | None

class ProgrammingLangauge(str, Enum):
    python = "python"
    javascript = "javascript"
    typescript = "typescript"

class Traceback(BaseModel):
    frames: List[TracebackFrame]
    message: str
    language: ProgrammingLangauge
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
            language=ProgrammingLangauge(ProgrammingLangauge.python),
            full_traceback=tbutil_parsed_exc.to_string(),
        )
    
class FileEdit(BaseModel):
    filepath: str
    range: Range
    replacement: str