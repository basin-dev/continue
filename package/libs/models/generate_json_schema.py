from .main import *
from .debug_context import SerializedDebugContext
from pydantic import schema_json_of
import os

MODELS_TO_GENERATE = [
    Position, Range, RangeInFile, Traceback, TracebackFrame, ProgrammingLangauge, FileEdit, CallGraph
] + [ SerializedDebugContext ]

RENAMES = {
    "SerializedDebugContext": "DebugContext"
}

SCHEMA_DIR = "schema"

def clear_schemas():
    for filename in os.listdir(SCHEMA_DIR):
        if filename.endswith(".json"):
            os.remove(os.path.join(SCHEMA_DIR, filename))

if __name__ == "__main__":
    clear_schemas()
    for model in MODELS_TO_GENERATE:
        title = RENAMES.get(model.__name__, model.__name__)
        try:
            json = schema_json_of(model, indent=2, title=title)
        except Exception as e:
            print(f"Failed to generate json schema for {title}: ", e)
            continue
        
        with open(f"{SCHEMA_DIR}/{title}.json", "w") as f:
            f.write(json)