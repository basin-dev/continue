import pluggy
from ...libs.steps import StepParams, Step, StepOutput

hookspec = pluggy.HookspecMarker("continue.step")

# Perhaps Actions should be generic about what their inputs must be.

class ActionPlugin(Step):
    @hookspec
    def run(self, params: StepParams) -> StepOutput:
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