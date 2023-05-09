from textwrap import dedent
from ...models.filesystem_edit import AddFile
from ..core import Step, ContinueSDK
from .main import WaitForUserInputStep


class EditReduxStateStep(Step):

    description: str  # e.g. "I want to load data from the weatherapi.com API"

    async def run(self, sdk: ContinueSDK):
        # Should be a way of locally storing (or later within the company)
        # some information, so you can ask the user the first time where the relevant folder is, and then it remembers this
        # but also what if it changes. So not such an interesting thing for now.

        # Find the 