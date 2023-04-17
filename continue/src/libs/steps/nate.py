from typing import Coroutine

from ...models.main import Range

from ...models.filesystem import RangeInFile
from ...models.filesystem_edit import AddDirectory, AddFile
from ..observation import Observation
from ..core import Step, StepParams
from .main import EditCodeStep
import os


class WritePytestsStep(Step):
    for_filepath: str
    instructions: str = "Write unit tests for this file."

    async def run(self, params: StepParams) -> Coroutine[Observation, None, None]:
        filename = os.path.basename(self.for_filepath)
        dirname = os.path.dirname(self.for_filepath)

        path_dir = os.path.join(dirname, "tests")
        if not os.path.exists(path_dir):
            await params.ide.applyFileSystemEdit(AddDirectory(path_dir))

        path = os.path.join(path_dir, f"test_{filename}")
        if os.path.exists(path):
            return None

        await params.ide.applyFileSystemEdit(AddFile(path, ""))

        prompt = f"""\
        # Write unit tests for {self.for_filepath}
        #
        # {self.instructions}
        #
        # {self.for_filepath}:
        #
        # ```python
        """
        await params.run_step(EditCodeStep(
            range_in_files=[RangeInFile(filepath=path, range=Range.from_shorthand(0, 0, 0, 0))], prompt=prompt))
