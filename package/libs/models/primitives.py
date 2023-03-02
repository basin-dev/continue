# The models in this file will not be generated, so should only be modifications of primitives for use in Python
# As of now, this file isn't being used.

from typing import Dict
from pydantic import BaseModel, validator, Extra
import os

class StrictBaseModel(BaseModel):
    class Config:
        extra = Extra.forbid

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
