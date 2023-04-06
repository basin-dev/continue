from typing import List
import pluggy
from pydantic import BaseModel
from ...models.filesystem import FileSystem
from ...libs.llm import LLM

hookspec = pluggy.HookspecMarker("continue.action")

class ActionParams(BaseModel):
    filesystem: FileSystem
    llm: LLM

@hookspec
def run(params: ActionParams):
    """Run an action

    :param cont: Continue SDK
    """

@hookspec
def can_handle(artifact_types: List[str]) -> bool:
    """Announce whether plugin can handle a combination of artifacts
    
    :param artifact_types: List of artifact types
    """