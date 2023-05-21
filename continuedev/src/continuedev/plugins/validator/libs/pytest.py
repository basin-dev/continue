from ....libs.traceback_parsers import parse_python_traceback
from ....libs.main import Artifact
from plugins import validator
from ..hookspecs import ValidatorParams, ValidatorReturn
import subprocess


@validator.hookimpl
def run(params: ValidatorParams) -> ValidatorReturn:
    result = subprocess.run(["pytest", "--tb=native"],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=sdk.root_dir)
    stdout = result.stdout.decode("utf-8")
    stderr = result.stderr.decode("utf-8")

    stdout_tb = parse_python_traceback(stdout)
    stderr_tb = parse_python_traceback(stderr)

    # If it fails, return the error
    if stdout_tb or stderr_tb:
        return False, Artifact(artifact_type="traceback", data=stdout_tb or stderr_tb)

    # If it succeeds, return None
    return True, None
