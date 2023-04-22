from typing import Coroutine
import pluggy
from ...libs.core import ContinueSDK, Step, Observation

hookspec = pluggy.HookspecMarker("continue.step")

# Perhaps Actions should be generic about what their inputs must be.


class StepPlugin(Step):
    @hookspec
    async def run(self, sdk: ContinueSDK) -> Coroutine[Observation, None, None]:
        """Run"""

# 1. Decide the action to take, which returns an Action *type*
# 2. Pass situational parameters to the Action type, to create an Action instance
# 3. Run the action instance by just calling without parameters
# 4. Apply the action's changes.

# @hookspec
# def can_handle(artifact_types: List[str]) -> bool:
#     """Announce whether plugin can handle a combination of artifacts

#     :param artifact_types: List of artifact types
#     """
