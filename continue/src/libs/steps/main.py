from typing import List
from ...models.main import Traceback, Range
from ..actions import FileSystemAction, FileEdit
from ...models.filesystem import RangeInFile
from ..llm.prompters import FormatStringPrompter
from ..llm.prompt_utils import MarkdownStyleEncoderDecoder
from textwrap import dedent
from ..steps import Step, StepParams, StepOutput
import subprocess
from ..util.traceback_parsers import parse_python_traceback
from ..observation import TracebackObservation

class RunCodeStep(Step):
    def __init__(self, cmd: str):
        self.cmd = cmd

    def run(self, params: StepParams) -> StepOutput:
        result = subprocess.run(params.run_cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=params.root_dir)
        stdout = result.stdout.decode("utf-8")
        stderr = result.stderr.decode("utf-8")
        print(stdout, stderr)

        # If it fails, return the error
        tb = parse_python_traceback(stdout) or parse_python_traceback(stderr)
        if tb:
            return TracebackObservation(traceback=tb), None
        else:
            return None, None

class SolveTracebackStep(Step):
    def __init__(self, traceback: Traceback):
        self.traceback = traceback

    # Step registers itself before as reversible/not
    # Step returns a plan (Edit/FileEdit/Action/Plan) that is marked as reversible/not
    # Both?
    # Do we ever need to know if a step is reversible BEFORE it is run? If not, fine to

    # So reversibility is the responsibility of the Step if it's doing something separate from FileSystemEdit.
    # What would this look like? Say making some API call.
    # It should define a resource?
    # Or should define an Edit/Action...an Action has an apply method and reverse if ReversibleAction

    # If a step is going to be reversible and call other reversible steps, it must be able to reverse itself after between all other called steps
    # That's gross, so then a step that uses other steps should just be defined in a special language, at its simplest just an array of steps in sequence.
    # OR we just say you can only make changes through a proxy, and the proxy "records" all changes. Then doesn't matter how things happen.
    # The FileSystem is the first example of this, maybe whats called a resource.
    # This makes it nicer that the Step can both take its actions in the moment AND return the EditDiff (actually probably the runner does this?)

    # I think there is no question as to whether you want Action and ReversibleAction. Only question is whether application is the responsibility of the Step
    # or the Runner. For now I'm going to go with the latter.

    def run(self, params: StepParams) -> StepOutput:
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

class ManualEditStep(Step):
    edit: FileSystemAction

    def __init__(self, edit: FileSystemAction):
        self.edit = edit

    def run(self, params: StepParams) -> List[FileEdit]:
        params.filesystem.apply_edit(self.edit)
        
# Instead of having to define a class, should be a create_action function, or Action.from()
# There should be an entire langauge-agnostic pipeline through the 1. running command, 2. parsing traceback, 3. generating edit


# Include the prompter inside of the encoder/decoder?
# Then you have layers -> LLM -> Prompter -> Encoder/Decoder
# Seems more like encoder/decoder should be subsumed by the prompter

# How to make actions composable??