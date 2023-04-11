from typing import Callable, List
from ...models.main import Traceback, Range
from ..actions import FileSystemAction, FileEdit
from ...models.filesystem import RangeInFile
from ..llm.prompters import FormatStringPrompter
from ..llm.prompt_utils import MarkdownStyleEncoderDecoder
from textwrap import dedent
from ..core import Step, StepParams, StepOutput, AtomicStep, Observation
import subprocess
from ..util.traceback_parsers import parse_python_traceback
from ..observation import TracebackObservation
from ..actions import SequentialAction

class RunCodeStep(AtomicStep):
    cmd: str

    def run(self, params: StepParams) -> StepOutput:
        result = subprocess.run(self.cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = result.stdout.decode("utf-8")
        stderr = result.stderr.decode("utf-8")
        print(stdout, stderr)

        # If it fails, return the error
        tb = parse_python_traceback(stdout) or parse_python_traceback(stderr)
        if tb:
            return TracebackObservation(traceback=tb), None
        else:
            return None, None
        
class EditCodeStep(AtomicStep):
    # Might make an even more specific atomic step, which is "apply file edit"
    range_in_files: List[RangeInFile]
    build_prompt: Callable[[str], str] # Function taking the code formatted as a string and generates the whole prompt. See SolveTracebackStep for an example.

    def run(self, params: StepParams) -> StepOutput:
        enc_dec = MarkdownStyleEncoderDecoder(filesystem=params.filesystem, range_in_files=self.range_in_files)
        code_string = enc_dec.encode()
        prompt = self.build_prompt(code_string)
        completion = params.llm.complete(prompt)
        file_edits = enc_dec.decode(completion)
        for file_edit in file_edits:
            file_edit.apply()

        return None, SequentialAction(actions=file_edits)

class SolveTracebackStep(Step):
    traceback: Traceback

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

    def run(self, params: StepParams) -> Observation:
        def build_prompt(code_string: str) -> str:
            return dedent("""I ran into this problem with my Python code:

                    {traceback}

                    Below are the files that might need to be fixed:

                    {code}

                    This is what the code should be in order to avoid the problem:
                """).format(traceback=self.traceback.full_traceback, code=code_string)
        
        range_in_files = []
        for frame in self.traceback.frames:
            range_in_files.append(RangeInFile.from_entire_file(frame.filepath, params.filesystem))

        params.runner.run(EditCodeStep(range_in_files=range_in_files, build_prompt=build_prompt))
        return None

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