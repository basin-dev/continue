from typing import Callable, List
from ...models.main import Traceback, Range
from ...models.filesystem_edit import EditDiff, FileSystemEdit
from ...models.filesystem import RangeInFile
from ..llm.prompt_utils import MarkdownStyleEncoderDecoder
from textwrap import dedent
from ..core import Policy, ReversibleStep, Step, StepParams, Observation, DoneStep
import subprocess
from ..util.traceback_parsers import parse_python_traceback
from ..observation import TracebackObservation


class RunPolicyUntilDoneStep(Step):
    policy: "Policy"

    def run(self, params: StepParams) -> Observation:
        next_step = self.policy.next(params.get_history())
        while next_step is not None and not isinstance(next_step, DoneStep):
            observation = params.run_step(next_step)
            next_step = self.policy.next(params.get_history())
        return observation


class RunCodeStep(Step):
    cmd: str

    def describe(self) -> str:
        return f"Run `{self.cmd}`"

    def run(self, params: StepParams) -> Observation:
        result = subprocess.run(
            self.cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = result.stdout.decode("utf-8")
        stderr = result.stderr.decode("utf-8")
        print(stdout, stderr)

        # If it fails, return the error
        tb = parse_python_traceback(stdout) or parse_python_traceback(stderr)
        if tb:
            return TracebackObservation(traceback=tb)
        else:
            return None


class EditCodeStep(ReversibleStep):
    # Might make an even more specific atomic step, which is "apply file edit"
    range_in_files: List[RangeInFile]
    prompt: str  # String with {code} somewhere

    _edit_diffs: List[EditDiff] = []

    def describe(self) -> str:
        return "Editing files: " + ", ".join(map(lambda rif: rif.filepath, self.range_in_files))
        # Description should be generated from the sub-steps. That, or can be defined specially by the developer with params.describe
        # To make the generator: By mixing runner and Step, you keep track of the Step's output as properties, which can be accessed after the yield (we can guarantee this)
        # so something like
        # next_step = SomeStep()
        # yield next_step
        # observation = next_step.observation
        # This is also nicer because it feels less like you're always taking the last step's observation only.

    def run(self, params: StepParams) -> Observation:
        enc_dec = MarkdownStyleEncoderDecoder(
            filesystem=params.filesystem, range_in_files=self.range_in_files)
        code_string = enc_dec.encode()
        prompt = self.prompt.format(code=code_string)
        completion = params.llm.complete(prompt)
        file_edits = enc_dec.decode(completion)
        for file_edit in file_edits:
            self._edit_diffs.append(params.filesystem.apply_edit(file_edit))

        return None

    def reverse(self, params: StepParams):
        for edit_diff in self._edit_diffs:
            params.filesystem.apply_edit(edit_diff.backward)


class FindCodeStep(Step):
    prompt: str

    def describe(self) -> str:
        return "Finding code"

    def run(self, params: StepParams) -> Observation:
        params.filesystem.open_files()


class UserInputStep(Step):
    user_input: str


class SolveTracebackStep(Step):
    traceback: Traceback

    def run(self, params: StepParams) -> Observation:
        prompt = dedent("""I ran into this problem with my Python code:

                {traceback}

                Below are the files that might need to be fixed:

                {code}

                This is what the code should be in order to avoid the problem:
            """).format(traceback=self.traceback.full_traceback, code="{code}")

        range_in_files = []
        for frame in self.traceback.frames:
            range_in_files.append(RangeInFile.from_entire_file(
                frame.filepath, params.filesystem))

        params.run_step(EditCodeStep(
            range_in_files=range_in_files, prompt=prompt))
        return None


class ManualEditStep(ReversibleStep):
    edit: FileSystemEdit
    _edit_diff: EditDiff

    def __init__(self, edit: FileSystemEdit):
        self.edit = edit

    def run(self, params: StepParams) -> Observation:
        self._edit_diff = params.filesystem.apply_edit(self.edit)

    def reverse(self, params: StepParams):
        params.filesystem.apply_edit(self._edit_diff)

# There should be an entire langauge-agnostic pipeline through the 1. running command, 2. parsing traceback, 3. generating edit


# Include the prompter inside of the encoder/decoder?
# Then you have layers -> LLM -> Prompter -> Encoder/Decoder
# Seems more like encoder/decoder should be subsumed by the prompter

# How to make actions composable??
