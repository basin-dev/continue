import asyncio
from textwrap import dedent
from typing import Coroutine

from ...models.main import Range
from ...models.filesystem import RangeInFile
from ...models.filesystem_edit import AddDirectory, AddFile
from ..observation import Observation
from ..core import Step, ContinueSDK
from .main import EditCodeStep, WaitForUserConfirmationStep
import os


class WritePytestsStep(Step):
    for_filepath: str | None = None
    instructions: str = "Write unit tests for this file."

    async def run(self, sdk: ContinueSDK) -> Coroutine[Observation, None, None]:
        if self.for_filepath is None:
            self.for_filepath = (await sdk.ide.getOpenFiles())[0]

        filename = os.path.basename(self.for_filepath)
        dirname = os.path.dirname(self.for_filepath)

        path_dir = os.path.join(dirname, "tests")
        if not os.path.exists(path_dir):
            await sdk.apply_filesystem_edit(AddDirectory(path=path_dir))

        path = os.path.join(path_dir, f"test_{filename}")
        if os.path.exists(path):
            return None

        for_file_contents = await sdk.ide.readFile(self.for_filepath)

        prompt = dedent(f"""\
        This is the file you will write unit tests for:

        ```python
        {for_file_contents}
        ```

        Here are additional instructions:

        "{self.instructions}"

        Here are the unit tests:

        """)
        tests = sdk.llm.complete(prompt)
        await sdk.apply_filesystem_edit(AddFile(filepath=path, content=tests))

        return None


class CreatePyplot(Step):
    # Wish there was a way to add import, specify dependency
    name: str = "Create a pyplot"

    async def run(self, sdk: ContinueSDK) -> Coroutine[Observation, None, None]:
        code = dedent("""import matplotlib.pyplot as plt
import numpy as np

{instructions}

plt.xlabel("{x_label}")
plt.ylabel("{y_label}")
plt.title("{title}")
plt.show()
        """)


class ImplementAbstractMethodStep(Step):
    name: str = "Implement abstract method for all subclasses"
    method_name: str = "def walk(self, path: str) -> List[str]"
    class_name: str = "FileSystem"

    async def run(self, sdk: ContinueSDK):
        await sdk.run_step(WaitForUserConfirmationStep(prompt="Detected new abstract method. Implement in all subclasses?"))
        implementations = []
        for filepath in ["/Users/natesesti/Desktop/continue/extension/examples/python/filesystem/real.py", "/Users/natesesti/Desktop/continue/extension/examples/python/filesystem/virtual.py"]:
            contents = await sdk.ide.readFile(filepath)
            implementations.append(
                RangeInFile.from_entire_file(filepath, contents))

        for implementation in implementations:
            await sdk.run_step(EditCodeStep(
                range_in_files=[implementation],
                prompt=f"{{code}}\nRewrite the class, implementing the method `{self.method_name}`.\n",
            ))
