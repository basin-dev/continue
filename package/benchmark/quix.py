import subprocess
from boltons import tbutils
from typing import Callable, List, Dict, Tuple
import os
import shutil
import signal
from ..server.debug import suggest_file_edits, find_sus_code, FindBody, DebugContext
from ..libs.virtual_filesystem import RealFileSystem
from ..libs.models.main import Traceback
from multiprocessing import Pool

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

# We keep an unchanging fo`lder, static_python_programs, and always create a temporary python_programs directory to be edited
python_programs_path = PATH_TO_QUIX_REPO + "/python_programs"
local_filesystem = RealFileSystem()
options = list_options()
timeout = 10
parallel = False

def run_option(option: str) -> Tuple[str, int]:
    # print(f"\33[1m\n\n------------------------------- Running {option} -------------------------------\n\n\033[0m")
    traceback = run_test(option, timeout)
    if traceback is None:
        print(f"Test {option} timed out.")
        return option, 0

    code_snippets = find_sus_code(traceback, local_filesystem, "")
    try:
        edits = suggest_file_edits(DebugContext(
            traceback=traceback,
            description="",
            ranges_in_files=code_snippets.response,
            filesystem=local_filesystem,
        ))
        for edit in edits:
            local_filesystem.apply_file_edit(edit)
    except Exception as e:
        print("Failed to generate edits: ", e,  "\n\n")
        return option, 1

    traceback = run_test(option, timeout)
    if traceback is None:
        print(f"\33[32mSuccessfully fixed {option}.\033[0m")
        return option, 2
    else:
        print(f"\033[91mFailed to fix {option}.\033[0m")
        return option, 3

if __name__ == "__main__":
    shutil.rmtree(python_programs_path, ignore_errors=True)
    shutil.copytree(PATH_TO_QUIX_REPO + "/static_python_programs", python_programs_path)

    timed_out = []
    failed = []
    successes = []
    not_success = []
    if parallel:
        with Pool() as pool:
            results = pool.map(run_option, options)
    else:
        results = [run_option(option) for option in options]

    for option, result in results:
        if result == 0:
            timed_out.append(option)
        elif result == 1:
            failed.append(option)
        elif result == 2:
            successes.append(option)
        elif result == 3:
            not_success.append(option)

    print("DONE!")
    print(f"{len(successes)}/{len(options)} successes: ", successes)
    print(f"{len(timed_out)}/{len(options)} timed out: ", timed_out)
    print(f"{len(failed)}/{len(options)} failed: ", failed)
    print(f"{len(not_success)}/{len(options)} not successful: ", not_success)


"""
- Timeouts
- Prompts
- Make sure call graphs are right
- Multiple tries? And try them all against the test.
"""