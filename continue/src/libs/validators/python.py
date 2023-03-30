from functools import partial
import re
from ..traceback_parsers import parse_python_traceback
from ...models.filesystem import FileSystem
from ..main import Validator, Artifact
import subprocess
from typing import Callable, Tuple
import ruff

# Might want to separate the parser ("Snooper") from the thing that runs the python program and receives stdout
# And might want to separate the traceback parser, because what if they are different for different python versions or something?
class PythonTracebackValidator(Validator):
    def __init__(self, cmd: str, cwd: str):
        self.cmd = cmd
        self.cwd = cwd

    def run(self, fs: FileSystem) -> Tuple[bool, Artifact]:
        # Run the python file
        result = subprocess.run(self.cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.cwd)
        stdout = result.stdout.decode("utf-8")
        stderr = result.stderr.decode("utf-8")
        print(stdout, stderr)

        # If it fails, return the error
        tb = parse_python_traceback(stdout) or parse_python_traceback(stderr)
        if tb:
            return False, Artifact(artifact_type="traceback", data=tb)
        
        # If it succeeds, return None
        return True, None
    
# Things get weird if you have to set up an environment to run. Make this part of cmd, the class, or the agent?
# Do you want to pass some context about the traceback and where it came from?
class PytestValidator(Validator):
    def __init__(self, cwd: str):
        self.cwd = cwd

    def run(self, fs: FileSystem) -> Tuple[bool, Artifact]:
        # Run the python file
        result = subprocess.run(["pytest", "--tb=native"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.cwd)
        stdout = result.stdout.decode("utf-8")
        stderr = result.stderr.decode("utf-8")

        stdout_tb = parse_python_traceback(stdout)
        stderr_tb = parse_python_traceback(stderr)

        # If it fails, return the error
        if stdout_tb or stderr_tb:
            return False, Artifact(artifact_type="traceback", data=stdout_tb or stderr_tb)
        
        # If it succeeds, return None
        return True, None
    
_ruff_regex = re.compile(r'(?P<filepath>.+):(?P<line_number>\d+):(?P<column_number>\d+): (?P<error>.+)')
class RuffValidator(Validator):
    def __init__(self, filepath: str):
        self.filepath = filepath

    def run(self, fs: FileSystem) -> Tuple[bool, Artifact]:
        result = subprocess.run(["ruff", "check", self.filepath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
    