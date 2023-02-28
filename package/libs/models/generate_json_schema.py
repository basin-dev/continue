from .main import *

MODELS_TO_GENERATE = [
    Position, Range, RangeInFile, SerializedVirtualFileSystem, Traceback, TracebackFrame, ProgrammingLangauge, FileEdit, CallGraph
]

if __name__ == "__main__":
    for model in MODELS_TO_GENERATE:
        try:
            json = model.schema_json(indent=2)
        except:
            print(f"Failed to generate json schema for {model.__name__}")
            continue
        
        with open(f"schema/{model.__name__}.json", "w") as f:
            f.write(json)