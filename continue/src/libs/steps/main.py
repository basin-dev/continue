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

    async def describe(self, llm: LLM) -> Coroutine[str, None, None]:
        return self.cmd

    async def run(self, sdk: ContinueSDK) -> Coroutine[Observation, None, None]:
        result = subprocess.run(
            self.cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd="/Users/natesesti/Desktop/continue/extension/examples/python")
        stdout = result.stdout.decode("utf-8")
        stderr = result.stderr.decode("utf-8")
        print(stdout, stderr)

        # If it fails, return the error
        if result.returncode != 0:
            return TextObservation(text=stdout)


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

        if "@dlt.resource" in prompt:
            time.sleep(3.5)
            completion = '''
```
import dlt
from dlt.sources.helpers import requests


@dlt.source
def weather_api_source(api_secret_key=dlt.secrets.value):
    return weather_api_resource(api_secret_key)


def _create_auth_headers(api_secret_key):
    """Constructs Bearer type authorization header which is the most common authorization method"""
    headers = {
        "Authorization": f"Bearer {api_secret_key}"
    }
    return headers


@dlt.resource(write_disposition="append")
def weather_api_resource(api_secret_key=dlt.secrets.value):
    headers = _create_auth_headers(api_secret_key)

    # check if authentication headers look fine

    # make an api call here
    url = 'https://api.weatherapi.com/v1/forecast.json'
    params = {'q': 'London', 'days': '7', 'key': api_secret_key}
    print(headers)
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    yield response.json()


if __name__ == '__main__':
    # configure the pipeline with your destination details
    pipeline = dlt.pipeline(pipeline_name='weather',
                            destination='duckdb', dataset_name='weather_api')

    # print credentials by running the resource
    data = list(weather_api_resource())

    # print the data yielded from resource
    print(data)
    exit()

    # run the pipeline with your parameters
    load_info = pipeline.run(weather_api_source())

    # pretty print the information on data that was loaded
    print(load_info)
```
            '''
        else:
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

        return None


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
