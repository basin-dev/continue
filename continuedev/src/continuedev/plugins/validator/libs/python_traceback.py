from ....libs.traceback_parsers import parse_python_traceback
from ....libs.main import Artifact
from plugins import validator
from ..hookspecs import ValidatorParams, ValidatorReturn
import subprocess

# Might want to separate the parser ("Snooper") from the thing that runs the python program and receives stdout
# And might want to separate the traceback parser, because what if they are different for different python versions or something?


@validator.hookimpl
def run(params: ValidatorParams) -> ValidatorReturn:
    # Run the python file
    result = subprocess.run(sdk.run_cmd.split(
    ), stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=sdk.root_dir)
    stdout = result.stdout.decode("utf-8")
    stderr = result.stderr.decode("utf-8")
    print(stdout, stderr)

    # If it fails, return the error
    tb = parse_python_traceback(stdout) or parse_python_traceback(stderr)
    if tb:
        return False, Artifact(artifact_type="traceback", data=tb)

    # If it succeeds, return None
    return True, None
