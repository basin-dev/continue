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

class AbsoluteFilePath(CustomStringModel):
    __root__: str

    @validator("__root__")
    def validate_path(cls, v):
        if not os.path.isabs(v):
            raise ValueError("Path must be absolute")
        return v

class Range(BaseModel):
    """A range in a file. 0-indexed."""
    startline: int
    endline: int
    startcol: int
    endcol: int

class RangeInFile(BaseModel):
    filepath: AbsoluteFilePath
    range: Range

class SerializedVirtualFileSystem(CustomDictModel):
    __root__: Dict[AbsoluteFilePath, str]

class TracebackFrame(BaseModel):
    filepath: AbsoluteFilePath
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

    @classmethod
    def from_tbutil_parsed_exc(cls, tbutil_parsed_exc):
        return cls(
            frames=[
                TracebackFrame(
                    filepath=AbsoluteFilePath(__root__=frame["filepath"]),
                    lineno=frame["lineno"],
                    function=frame["funcname"],
                    code=frame["source_line"],
                )
                for frame in tbutil_parsed_exc.frames
            ],
            message=tbutil_parsed_exc.exc_msg,
            language=ProgrammingLangauge(ProgrammingLangauge.python),
        )