from typing import Dict, List
from pydantic import BaseModel
import difflib

class Position(BaseModel):
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
    
class FileEdit(BaseModel):
    filepath: str
    range: Range
    replacement: str
        

class EditDiff(BaseModel):
    """A reversible edit that can be applied to a file."""
    edit: FileEdit
    original: str