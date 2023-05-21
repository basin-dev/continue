import re
from ....libs.main import Artifact
import subprocess
from plugins import validator
from ..hookspecs import ValidatorParams, ValidatorReturn

_ruff_regex = re.compile(
    r'(?P<filepath>.+):(?P<line_number>\d+):(?P<column_number>\d+): (?P<error>.+)')


@validator.hookimpl
def run(params: ValidatorParams) -> ValidatorReturn:
    result = subprocess.run(["ruff", "check", sdk.root_dir],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = result.stdout.decode("utf-8")

    lines = stdout.splitlines()
    if len(lines) == 0:
        return True, None

    data = []
    for line in lines:
        match = _ruff_regex.match(line)
        if match:
            data.append(match.groupdict())

    return False, Artifact(artifact_type="ruff", data=data)
