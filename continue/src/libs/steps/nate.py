from textwrap import dedent
from typing import Coroutine

from ...models.main import Range

from ...models.filesystem import RangeInFile
from ...models.filesystem_edit import AddDirectory, AddFile
from ..observation import Observation
from ..core import Step, StepParams
from .main import EditCodeStep
import os


class WritePytestsStep(Step):
    for_filepath: str | None = None
    instructions: str = "Write unit tests for this file."

    async def run(self, params: StepParams) -> Coroutine[Observation, None, None]:
        if self.for_filepath is None:
            self.for_filepath = (await params.ide.getOpenFiles())[0]

        filename = os.path.basename(self.for_filepath)
        dirname = os.path.dirname(self.for_filepath)

        path_dir = os.path.join(dirname, "tests")
        if not os.path.exists(path_dir):
            await params.ide.applyFileSystemEdit(AddDirectory(path=path_dir))

        path = os.path.join(path_dir, f"test_{filename}")
        if os.path.exists(path):
            return None

        for_file_contents = await params.ide.readFile(self.for_filepath)

        prompt = dedent(f"""\
        This is the file you will write unit tests for:

        ```python
        {for_file_contents}
        ```

        Here are additional instructions:

        "{self.instructions}"

        Here are the unit tests:

        """)
        tests = params.llm.complete(prompt)
        await params.ide.applyFileSystemEdit(AddFile(filepath=path, content=tests))

        return None
