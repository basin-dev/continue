from typing import Dict, List
from pydantic import BaseModel
from enum import Enum
from .primitives import StrictBaseModel

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

class RangeInFile(StrictBaseModel):
    filepath: str
    range: Range

    def __hash__(self):
        return hash((self.filepath, self.range))

# class SerializedVirtualFileSystem(CustomDictModel):
    # __root__: Dict[AbsoluteFilePath, str]

SerializedVirtualFileSystem = Dict[str, str]

class TracebackFrame(StrictBaseModel):
    filepath: str
    lineno: int
    function: str
    code: str | None

    def __eq__(self, other):
        return self.filepath == other.filepath and self.lineno == other.lineno and self.function == other.function

class ProgrammingLangauge(str, Enum):
    python = "python"
    javascript = "javascript"
    typescript = "typescript"

class Traceback(StrictBaseModel):
    frames: List[TracebackFrame]
    message: str
    error_type: str
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
            error_type=tbutil_parsed_exc.exc_type,
            language=ProgrammingLangauge(ProgrammingLangauge.python),
            full_traceback=tbutil_parsed_exc.to_string(),
        )
    
class FileEdit(StrictBaseModel):
    filepath: str
    range: Range
    replacement: str

class CallGraph(StrictBaseModel):
    """A call graph of a function."""
    function_name: str
    function_range: RangeInFile
    calls: List['CallGraph']

    def get_all_ranges(self) -> List[RangeInFile]:
        return list(set([self.function_range] + sum([call.get_all_ranges() for call in self.calls], [])))
    
    def pretty_print(self) -> str:
        return self.function_name + "\n  " + "\n  ".join(list(map(lambda call: call.pretty_print(), self.calls)))