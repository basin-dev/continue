from typing import List
from ...models.main import FileEdit, FileSystemEdit, Traceback, Range
from ...models.filesystem import RangeInFile
from ..main import Action, ActionParams
from .llm.prompters import FormatStringPrompter
from .llm.prompt_utils import MarkdownStyleEncoderDecoder
from textwrap import dedent

class SolveTracebackAction(Action):
    def __init__(self, traceback: Traceback):
        self.traceback = traceback

    def run(self, params: ActionParams) -> List[FileEdit]:
        prompter = FormatStringPrompter(dedent("""I ran into this problem with my Python code:

        {traceback}

        Below are the files that might need to be fixed:

        {code}

        This is what the code should be in order to avoid the problem:
    """), llm=params.llm)
        
        range_in_files = []
        for frame in self.traceback.frames:
            range_in_files.append(RangeInFile.from_entire_file(frame.filepath, params.filesystem))

        print("Traceback frames: ", self.traceback.frames)
        print("Range in files: ", range_in_files)

        enc_dec = MarkdownStyleEncoderDecoder(params.filesystem, range_in_files)
        completion = prompter.complete({
            "code": enc_dec.encode(),
            "traceback": self.traceback.full_traceback
        })
        print(completion)
        file_edits = enc_dec.decode(completion)
        print(file_edits)
        print("****************")
        return file_edits

class ManualEditAction(Action):
    edit: FileSystemEdit

    def __init__(self, edit: FileSystemEdit):
        self.edit = edit

    def run(self, params: ActionParams) -> List[FileEdit]:
        params.filesystem.apply_edit(self.edit)
        

# Instead of having to define a class, should be a create_action function, or Action.from()
# There should be an entire langauge-agnostic pipeline through the 1. running command, 2. parsing traceback, 3. generating edit


# Include the prompter inside of the encoder/decoder?
# Then you have layers -> LLM -> Prompter -> Encoder/Decoder
# Seems more like encoder/decoder should be subsumed by the prompter

# How to make actions composable??