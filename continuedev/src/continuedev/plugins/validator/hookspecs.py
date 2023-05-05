from typing import List, Tuple
import pluggy
from ...libs.main import Artifact
from ...models.filesystem import FileSystem
from pydantic import BaseModel

hookspec = pluggy.HookspecMarker("continue.validator")

class ValidatorParams(BaseModel):
    filesystem: FileSystem
    root_dir: str
    run_cmd: str

ValidatorReturn = Tuple[bool, Artifact]

@hookspec
def run(params: ValidatorParams) -> ValidatorReturn:
    """Run a validator

    :param fs: Filesystem
    :return: Tuple of (bool, Artifact) where bool is whether the validator passed and Artifact is the artifact that was created
    """