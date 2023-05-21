from textwrap import dedent
from ...models.filesystem_edit import AddFile
from ..core import Step, ContinueSDK
from .main import WaitForUserInputStep, EditFileStep


class EditReduxStateStep(Step):

    description: str  # e.g. "I want to load data from the weatherapi.com API"

    async def run(self, sdk: ContinueSDK):
        # Should be a way of locally storing (or later within the company)
        # some information, so you can ask the user the first time where the relevant folder is, and then it remembers this
        # but also what if it changes. So not such an interesting thing for now.

        # Find the redux folder, or the files where this happens.
        # This means you need a way to view the filetree. Or select a file within the notebook?

        # Find the right file to edit
        # RootStore
        store_filename = ""
        sdk.run_step(
            EditFileStep(
                filename=store_filename,
                prompt=f"Edit the root store to add a new slice for {self.description}"
            )
        )
        store_file_contents = await sdk.ide.readFile(store_filename)
        # The EditFileStep should return the new contents of the file, so you can use it in the next step.

        # Selector
        selector_filename = ""
        sdk.run_step(EditFileStep(
            filepath=selector_filename,
            prompt=f"Edit the selector to add a new property for {self.description}. The store looks like this: {store_file_contents}"
        )

        # Reducer
        reducer_filename = ""
        sdk.run_step(EditFileStep(
            filepath=reducer_filename,
            prompt=f"Edit the reducer to add a new property for {self.description}. The store looks like this: {store_file_contents}"

        """
        Starts with implementing selector?
        1. RootStore
        2. Selector
        3. Reducer or entire slice

        Need to first determine whether this is a:
        1. edit
        2. add new reducer and property in existing slice
        3. add whole new slice
        4. build redux from scratch

        Let's say it's 2 for now. Later can have multiple substeps.
        """
