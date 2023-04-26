import time
from typing import Callable, Coroutine, List

from ..llm import LLM
from ...models.main import Traceback, Range
from ...models.filesystem_edit import EditDiff
from ...models.filesystem import RangeInFile, RangeInFileWithContents
from ..observation import Observation, TextObservation
from ..llm.prompt_utils import MarkdownStyleEncoderDecoder
from textwrap import dedent
from ..core import History, Policy, Step, ContinueSDK, Observation
import subprocess
from ..util.traceback_parsers import parse_python_traceback
from ..observation import TracebackObservation


class RunPolicyUntilDoneStep(Step):
    policy: "Policy"

    async def run(self, sdk: ContinueSDK) -> Coroutine[Observation, None, None]:
        next_step = self.policy.next(sdk.history)
        while next_step is not None:
            observation = await sdk.run_step(next_step)
            next_step = self.policy.next(sdk.history)
        return observation


class RunCommandStep(Step):
    cmd: str
    name: str = "Run command"
    _description: str = None

    async def describe(self, llm: LLM) -> Coroutine[str, None, None]:
        if self._description is not None:
            return self._description
        return self.cmd

    async def run(self, sdk: ContinueSDK) -> Coroutine[Observation, None, None]:
        cwd = await sdk.ide.getWorkspaceDirectory()
        result = subprocess.run(
            self.cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
        stdout = result.stdout.decode("utf-8")
        stderr = result.stderr.decode("utf-8")
        print(stdout, stderr)

        # If it fails, return the error
        if result.returncode != 0:
            return TextObservation(text=stderr)
        else:
            return TextObservation(text=stdout)


def ShellCommandsStep(Step):
    cmds: List[str]
    name: str = "Run Shell Commands"

    async def describe(self, llm: LLM) -> Coroutine[str, None, None]:
        return "\n".join(self.cmds)

    async def run(self, sdk: ContinueSDK) -> Coroutine[Observation, None, None]:
        cwd = await sdk.ide.getWorkspaceDirectory()

        process = subprocess.Popen(
            '/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE, cwd=cwd)

        stdin_input = "\n".join(self.cmds)
        out, err = process.communicate(stdin_input.encode())

        # If it fails, return the error
        if err is not None and err != "":
            return TextObservation(text=err)

        return None


class WaitForUserInputStep(Step):
    prompt: str
    name: str = "Waiting for user input"

    _description: str | None = None

    async def describe(self, llm: LLM) -> Coroutine[str, None, None]:
        return self.prompt

    async def run(self, sdk: ContinueSDK) -> Coroutine[Observation, None, None]:
        self._description = self.prompt
        resp = await sdk.wait_for_user_input()
        return TextObservation(text=resp)


class WaitForUserConfirmationStep(Step):
    prompt: str
    name: str = "Waiting for user confirmation"

    async def describe(self, llm: LLM) -> Coroutine[str, None, None]:
        return self.prompt

    async def run(self, sdk: ContinueSDK) -> Coroutine[Observation, None, None]:
        self._description = self.prompt
        resp = await sdk.wait_for_user_input()
        return TextObservation(text=resp)


class RunCodeStep(Step):
    cmd: str

    async def describe(self, llm: LLM) -> Coroutine[str, None, None]:
        return f"Ran command: `{self.cmd}`"

    async def run(self, sdk: ContinueSDK) -> Coroutine[Observation, None, None]:
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


demo_completions = {
    "File (/Users/natesesti/Desktop/continue/extension/examples/python/filesystem/real.py)": '''import os
from typing import List
from filesystem.filesystem import FileSystem


class RealFileSystem(FileSystem):
    """A filesystem that reads/writes from the actual filesystem."""

    def read(self, path) -> str:
        with open(path, "r") as f:
            return f.read()

    def readlines(self, path) -> List[str]:
        with open(path, "r") as f:
            return f.readlines()

    def write(self, path, content):
        with open(path, "w") as f:
            f.write(content)

    def exists(self, path) -> bool:
        return os.path.exists(path)

    def rename_file(self, filepath: str, new_filepath: str):
        os.rename(filepath, new_filepath)

    def rename_directory(self, path: str, new_path: str):
        os.rename(path, new_path)

    def delete_file(self, filepath: str):
        os.remove(filepath)

    def add_directory(self, path: str):
        os.makedirs(path)
    
    def walk(self, path: str) -> List[str]:
        file_list = []
        for root, dirs, files in os.walk(path):
            for f in files:
                file_list.append(os.path.join(root, f))
        return file_list
    ''',
    "File (/Users/natesesti/Desktop/continue/extension/examples/python/filesystem/virtual.py)": '''from typing import Dict, List
from filesystem.filesystem import FileSystem


class VirtualFileSystem(FileSystem):
    """A simulated filesystem from a mapping of filepath to file contents."""
    files: Dict[str, str]

    def __init__(self, files: Dict[str, str]):
        self.files = files

    def read(self, path) -> str:
        return self.files[path]

    def readlines(self, path) -> List[str]:
        return self.files[path].splitlines()

    def write(self, path, content):
        self.files[path] = content

    def exists(self, path) -> bool:
        return path in self.files

    def rename_file(self, filepath: str, new_filepath: str):
        self.files[new_filepath] = self.files[filepath]
        del self.files[filepath]

    def rename_directory(self, path: str, new_path: str):
        for filepath in self.files:
            if filepath.startswith(path):
                new_filepath = new_path + filepath[len(path):]
                self.files[new_filepath] = self.files[filepath]
                del self.files[filepath]

    def delete_file(self, filepath: str):
        del self.files[filepath]

    def add_directory(self, path: str):
        pass
    
    def walk(self, path: str) -> List[str]:
        return [filepath for filepath in self.files if filepath.startswith(path)]
    '''
}


class EditCodeStep(Step):
    # Might make an even more specific atomic step, which is "apply file edit"
    range_in_files: List[RangeInFile]
    prompt: str  # String with {code} somewhere
    name: str = "Edit code"

    _edit_diffs: List[EditDiff] | None = None
    _prompt: str | None = None
    _completion: str | None = None

    async def describe(self, llm: LLM) -> Coroutine[str, None, None]:
        if self._edit_diffs is None:
            return "Editing files: " + ", ".join(map(lambda rif: rif.filepath, self.range_in_files))
        elif len(self._edit_diffs) == 0:
            return "No edits made"
        else:
            return llm.complete(dedent(f"""{self._prompt}{self._completion}

                Maximally concise summary of changes in bullet points (can use markdown):
            """))

        # Description should be generated from the sub-steps. That, or can be defined specially by the developer with sdk.describe
        # To make the generator: By mixing runner and Step, you keep track of the Step's output as properties, which can be accessed after the yield (we can guarantee this)
        # so something like
        # next_step = SomeStep()
        # yield next_step
        # observation = next_step.observation
        # This is also nicer because it feels less like you're always taking the last step's observation only.

    async def run(self, sdk: ContinueSDK) -> Coroutine[Observation, None, None]:
        rif_with_contents = []
        for range_in_file in self.range_in_files:
            file_contents = await sdk.ide.readRangeInFile(range_in_file)
            rif_with_contents.append(
                RangeInFileWithContents.from_range_in_file(range_in_file, file_contents))
        enc_dec = MarkdownStyleEncoderDecoder(rif_with_contents)
        code_string = enc_dec.encode()
        prompt = self.prompt.format(code=code_string)

        used_demo = False
        for demo_prompt, demo_completion in demo_completions.items():
            if demo_prompt in prompt:
                used_demo = True
                completion = demo_completion
                time.sleep(1.5)
                break

        if not used_demo:
            completion = sdk.llm.complete(prompt)

        # Temporarily doing this to generate description.
        self._prompt = prompt
        self._completion = completion

        file_edits = enc_dec.decode(completion)

        self._edit_diffs = []
        for file_edit in file_edits:
            diff = await sdk.apply_filesystem_edit(file_edit)
            self._edit_diffs.append(diff)

        for filepath in set([file_edit.filepath for file_edit in file_edits]):
            await sdk.ide.saveFile(filepath)
            await sdk.ide.setFileOpen(filepath)

        return None


class EditFileStep(Step):
    filepath: str
    prompt: str
    hide: bool = True

    async def describe(self, llm: LLM) -> Coroutine[str, None, None]:
        return "Editing file: " + self.filepath

    async def run(self, sdk: ContinueSDK) -> Coroutine[Observation, None, None]:
        file_contents = await sdk.ide.readFile(self.filepath)
        await sdk.run_step(EditCodeStep(
            range_in_files=[RangeInFile.from_entire_file(
                self.filepath, file_contents)],
            prompt=self.prompt
        ))


class EditHighlightedCodeStep(Step):
    user_input: str
    hide = True
    _prompt: str = dedent("""Below is the code before changes:

{code}

This is the user request:

{user_input}

This is the code after being changed to perfectly satisfy the user request:
    """)

    async def describe(self, llm: LLM) -> Coroutine[str, None, None]:
        return "Editing highlighted code"

    async def run(self, sdk: ContinueSDK) -> Coroutine[Observation, None, None]:
        range_in_files = await sdk.ide.getHighlightedCode()
        if len(range_in_files) == 0:
            # Get the full contents of all open files
            files = await sdk.ide.getOpenFiles()
            contents = {}
            for file in files:
                contents[file] = await sdk.ide.readFile(file)

            range_in_files = [RangeInFile.from_entire_file(
                filepath, content) for filepath, content in contents.items()]

        await sdk.run_step(EditCodeStep(
            range_in_files=range_in_files, prompt=self._prompt.format(code="{code}", user_input=self.user_input)))


class FindCodeStep(Step):
    prompt: str

    async def describe(self, llm: LLM) -> Coroutine[str, None, None]:
        return "Finding code"

    async def run(self, sdk: ContinueSDK) -> Coroutine[Observation, None, None]:
        return await sdk.ide.getOpenFiles()


class UserInputStep(Step):
    user_input: str


class SolveTracebackStep(Step):
    traceback: Traceback

    async def describe(self, llm: LLM) -> Coroutine[str, None, None]:
        return f"```\n{self.traceback.full_traceback}\n```"

    async def run(self, sdk: ContinueSDK) -> Coroutine[Observation, None, None]:
        prompt = dedent("""I ran into this problem with my Python code:

                {traceback}

                Below are the files that might need to be fixed:

                {code}

                This is what the code should be in order to avoid the problem:
            """).format(traceback=self.traceback.full_traceback, code="{code}")

        range_in_files = []
        for frame in self.traceback.frames:
            content = await sdk.ide.readFile(frame.filepath)
            range_in_files.append(
                RangeInFile.from_entire_file(frame.filepath, content))

        await sdk.run_step(EditCodeStep(
            range_in_files=range_in_files, prompt=prompt))
        return None

# There should be an entire langauge-agnostic pipeline through the 1. running command, 2. parsing traceback, 3. generating edit


# Include the prompter inside of the encoder/decoder?
# Then you have layers -> LLM -> Prompter -> Encoder/Decoder
# Seems more like encoder/decoder should be subsumed by the prompter

# How to make actions composable??
