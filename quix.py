import subprocess
from boltons import tbutils
from typing import Callable, List, Dict, Tuple
import os
import shutil
import json
import signal
from debug import edit, find_sus_code, FindModel, DebugContext

PATH_TO_QUIX_REPO = "/Users/natesesti/Desktop/basin/QuixBugs"

def parse_first_stacktrace(stdout: str) -> None | List[Dict]:
    lines = stdout.splitlines()
    for i in range(len(lines)):
        if (lines[i].startswith("Traceback (most recent call last):")):
            break
    
    if i >= len(lines) - 1:
        return None
    
    for j in range(i + 1, len(lines)):
        if lines[j].strip()[0] == lines[j][0]:
            break
    
    stdout = "\n".join(lines[i:j + 1])
    return tbutils.ParsedException.from_string(stdout)

def list_options():
    files = os.listdir(PATH_TO_QUIX_REPO + "/python_programs")
    return list(map(lambda filename: filename.split(".")[0], files))

def run_test(option: str, timeout: int | None=None) -> tbutils.ParsedException:
    os.chdir(PATH_TO_QUIX_REPO)
    command = ["pytest", f"python_testcases/test_{option}.py", "--tb=native"]
    if timeout is not None:
        stdout = exec_command_with_timeout(command, timeout)
    else:
        stdout = subprocess.run(command, capture_output=True).stdout.decode("utf-8")
    if stdout is None:
        return None
    stacktrace = parse_first_stacktrace(stdout)
    return stacktrace

def exec_command_with_timeout(command: List[str], seconds: int) -> str | None:
    def handler(signum, frame):
        raise TimeoutError("Timed out!")

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(seconds)
    try:
        return subprocess.run(command, capture_output=True).stdout.decode("utf-8")
    except:
        return None
    finally:
        signal.alarm(0)

def main():
    # We keep an unchanging folder, static_python_programs, and always create a temporary python_programs directory to be edited
    python_programs_path = PATH_TO_QUIX_REPO + "/python_programs"
    shutil.rmtree(python_programs_path, ignore_errors=True)
    shutil.copytree(PATH_TO_QUIX_REPO + "/static_python_programs", python_programs_path)
    
    outcomes = {}
    for option in list_options():   
        print("Running", option)
        stacktrace = run_test(option, 2)
        if stacktrace is None:
            print(f"Test {option} timed out.")
            continue

        filepath = f"{PATH_TO_QUIX_REPO}/python_programs/{option}.py"
        print("Stacktrace: ", stacktrace.to_string() + "\n")
        code_snippets = find_sus_code(FindModel(**{
            "stacktrace": stacktrace.to_string(),
            "description": "",
            "files": {
                filepath: open(filepath, "r").read(),
            },
        }))

        edited_code = edit(DebugContext(**{
            "stacktrace": stacktrace.to_string(),
            "description": "",
            "code": list(map(lambda x: x['code'], code_snippets["response"])),
        }))['completion']
        print("Edited code: ", edited_code)

        with open(filepath, "w") as f:
            f.write(edited_code)

        outcomes[option] = edited_code

    print(json.dumps(outcomes, indent=2))

if __name__ == "__main__":
    main()

"""
Benchmarking:
0. Copy the bad python folder to a temporary folder where you will make edits
1. Run the test on the failing code
2. Pass the stacktrace and code to an edit generator
3. Make the edit on a copy of the file
"""