import subprocess
from boltons import tbutils
from typing import Callable, List, Dict, Tuple
import os
import shutil
import signal
from ..server.debug import suggest_file_edits, find_sus_code, FindBody, DebugContext
from ..libs.virtual_filesystem import RealFileSystem
from ..libs.models import Traceback

PATH_TO_QUIX_REPO = "/Users/natesesti/Desktop/basin/QuixBugs"

def parse_first_traceback(stdout: str) -> None | Traceback:
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

    tbutil_parsed = tbutils.ParsedException.from_string(stdout)
    if tbutil_parsed is None:
        return None
    return Traceback.from_tbutil_parsed_exc(tbutil_parsed)

def list_options():
    files = os.listdir(PATH_TO_QUIX_REPO + "/python_programs")
    return list(map(lambda filename: filename.split(".")[0], files))

def run_test(option: str, timeout: int | None=None) -> Traceback | None:
    os.chdir(PATH_TO_QUIX_REPO)
    command = ["pytest", f"python_testcases/test_{option}.py", "--tb=native"]
    if timeout is not None:
        stdout = exec_command_with_timeout(command, timeout)
    else:
        stdout = subprocess.run(command, capture_output=True).stdout.decode("utf-8")
    if stdout is None:
        return None
    traceback = parse_first_traceback(stdout)
    return traceback

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
    local_filesystem = RealFileSystem()
    
    successes = []
    options = list_options()[2:3]
    for option in options:   
        print("Running", option)
        traceback = run_test(option, 2)
        if traceback is None:
            print(f"Test {option} timed out.")
            continue

        filepath = f"{PATH_TO_QUIX_REPO}/python_programs/{option}.py"
        print("Stacktrace: ", traceback.full_traceback + "\n")
        code_snippets = find_sus_code(traceback, local_filesystem, "")

        print("Code Snippets: ", code_snippets.response)
        continue

        try:
            edits = suggest_file_edits(DebugContext(
                traceback=traceback,
                description="",
                ranges_in_files=code_snippets.response,
                filesystem=local_filesystem,
            ))
        except Exception as e:
            print("Failed to generate edits: ", e + "\n\n")
            continue

        for edit in edits:
            local_filesystem.apply_file_edit(edit)

        traceback = run_test(option, 2)
        if traceback is None:
            print(f"Successfully fixed {option}.")
            successes.append(option)
            continue
        print("\n\nAfter Fixing: ", traceback.full_traceback + "\n\n")

    print("DONE!")
    print(f"{len(successes)}/{len(options)} successes: ", successes)

if __name__ == "__main__":
    main()

"""
Benchmarking:
0. Copy the bad python folder to a temporary folder where you will make edits
1. Run the test on the failing code
2. Pass the traceback and code to an edit generator
3. Make the edit on a copy of the file
"""