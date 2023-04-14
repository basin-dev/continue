from typing import Union
from ..models.main import *
from ..models.filesystem import *
from ..libs.core import History, HistoryNode, Observation
from pydantic import schema_json_of
import os

# FileSystemEdit = Union[AddFile, DeleteFile, RenameFile, AddDirectory, DeleteDirectory, RenameDirectory, EditDiff]

# Can be a pydantic type, or a tuple of (title, pydantic type)
MODELS_TO_GENERATE = [
    Position, Range, Traceback, TracebackFrame
] + [
    RangeInFile,  # FileEdit, AddFile, DeleteFile, RenameFile, AddDirectory, DeleteDirectory, RenameDirectory, EditDiff
] + [
    History, HistoryNode, Observation
]
# + [
#     ("FileSystemEdit", FileSystemEdit)
# ]

RENAMES = {
    "SerializedDebugContext": "DebugContext"
}

SCHEMA_DIR = "schema/json"


def clear_schemas():
    for filename in os.listdir(SCHEMA_DIR):
        if filename.endswith(".json"):
            os.remove(os.path.join(SCHEMA_DIR, filename))


if __name__ == "__main__":
    clear_schemas()
    for model in MODELS_TO_GENERATE:
        if type(model) == tuple:
            title = model[0]
            model = model[1]
        else:
            title = model.__name__
        try:
            json = schema_json_of(model, indent=2, title=title)
        except Exception as e:
            print(f"Failed to generate json schema for {title}: ", e)
            continue

        with open(f"{SCHEMA_DIR}/{title}.json", "w") as f:
            f.write(json)
