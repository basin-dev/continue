from typing import Callable, Coroutine, List

from ..llm import LLM
from ...models.main import Traceback, Range
from ...models.filesystem_edit import EditDiff, FileSystemEdit, SequentialFileSystemEdit
from ...models.filesystem import RangeInFile
from ..llm.prompt_utils import MarkdownStyleEncoderDecoder
from textwrap import dedent
from ..core import Policy, ReversibleStep, Step, StepParams, Observation, DoneStep
import subprocess
from ..util.traceback_parsers import parse_python_traceback
from ..observation import TracebackObservation


class RunPolicyUntilDoneStep(Step):
    policy: "Policy"

    async def run(self, params: StepParams) -> Coroutine[Observation, None, None]:
        next_step = self.policy.next(params.get_history())
        while next_step is not None and not isinstance(next_step, DoneStep):
            observation = await params.run_step(next_step)
            next_step = self.policy.next(params.get_history())
        return observation


class RunCodeStep(Step):
    cmd: str

    async def describe(self, llm: LLM) -> str:
        return f"Ran command: `{self.cmd}`"

    async def run(self, params: StepParams) -> Coroutine[Observation, None, None]:
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
            self.hide = True
            return None


class EditCodeStep(ReversibleStep):
    # Might make an even more specific atomic step, which is "apply file edit"
    range_in_files: List[RangeInFile]
    prompt: str  # String with {code} somewhere
    name: str = "Edit code"

    _edit_diffs: List[EditDiff] | None = None
    _prompt: str | None = None
    _completion: str | None = None

    async def describe(self, llm: LLM) -> str:
        if self._edit_diffs is None:
            return "Editing files: " + ", ".join(map(lambda rif: rif.filepath, self.range_in_files))
        elif len(self._edit_diffs) == 0:
            return "No edits made"
        else:
            return llm.complete(dedent(f"""{self._prompt}{self._completion}

                Maximally concise summary of changes in bullet points (can use markdown):
            """))

        # Description should be generated from the sub-steps. That, or can be defined specially by the developer with params.describe
        # To make the generator: By mixing runner and Step, you keep track of the Step's output as properties, which can be accessed after the yield (we can guarantee this)
        # so something like
        # next_step = SomeStep()
        # yield next_step
        # observation = next_step.observation
        # This is also nicer because it feels less like you're always taking the last step's observation only.

    async def run(self, params: StepParams) -> Coroutine[Observation, None, None]:
        enc_dec = MarkdownStyleEncoderDecoder(
            filesystem=params.filesystem, range_in_files=self.range_in_files)
        code_string = enc_dec.encode()
        prompt = self.prompt.format(code=code_string)
        completion = params.llm.complete(prompt)

        # Temporarily doing this to generate description.
        self._prompt = prompt
        self._completion = completion

        file_edits = enc_dec.decode(completion)

        self._edit_diffs = []
        for file_edit in file_edits:
            self._edit_diffs.append(params.filesystem.apply_edit(file_edit))

        return None

    def reverse(self, params: StepParams):
        for edit_diff in self._edit_diffs:
            params.filesystem.apply_edit(edit_diff.backward)


class EditHighlightedCodeStep(Step):
    user_input: str
    hide = True
    _prompt: str = dedent("""Below is the code before changes:

                {code}

                This is the user request:

                {user_input}

                This is the code after being changed to perfectly satisfy the user request:
            """)

    async def describe(self, llm: LLM) -> str:
        return "Editing highlighted code"

    async def run(self, params: StepParams) -> Coroutine[Observation, None, None]:
        range_in_files = await params.ide.getHighlightedCode()
        if len(range_in_files) == 0:
            files = await params.ide.getOpenFiles()
            range_in_files = [RangeInFile.from_entire_file(
                filepath, params.filesystem) for filepath in files]

        await params.run_step(EditCodeStep(
            range_in_files=range_in_files, prompt=self._prompt.format(code="{code}", user_input=self.user_input)))


# class SuggestHighlightedCodeStep(Step):
#     user_input: str
#     hide = True
#     _prompt: str = dedent("""Below is the code before changes:

#                 {code}

#                 This is the user request:

#                 {user_input}

#                 This is the code after being changed to perfectly satisfy the user request:
#             """)

#     async def describe(self, llm: LLM) -> str:
#         return "Making suggestion to change highlighted code"

#     async def run(self, params: StepParams) -> Coroutine[Observation, None, None]:
#         range_in_files = await params.ide.getHighlightedCode()
#         if len(range_in_files) == 0:
#             files = await params.ide.getOpenFiles()
#             range_in_files = [RangeInFile.from_entire_file(
#                 filepath, params.filesystem) for filepath in files]

#         params.ide.showSuggestion()
#         await params.run_step(EditCodeStep(
#             range_in_files=range_in_files, prompt=self._prompt.format(code="{code}", user_input=self.user_input)))


class FindCodeStep(Step):
    prompt: str

    async def describe(self, llm: LLM) -> str:
        return "Finding code"

    async def run(self, params: StepParams) -> Coroutine[Observation, None, None]:
        params.filesystem.open_files()


class UserInputStep(Step):
    user_input: str


class SolveTracebackStep(Step):
    traceback: Traceback

    async def run(self, params: StepParams) -> Coroutine[Observation, None, None]:
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

        await params.run_step(EditCodeStep(
            range_in_files=range_in_files, prompt=prompt))
        return None

# There should be an entire langauge-agnostic pipeline through the 1. running command, 2. parsing traceback, 3. generating edit


# Include the prompter inside of the encoder/decoder?
# Then you have layers -> LLM -> Prompter -> Encoder/Decoder
# Seems more like encoder/decoder should be subsumed by the prompter

# How to make actions composable??
