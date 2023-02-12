import subprocess
from boltons import tbutils
from typing import List, Dict
import os
import shutil
import json
from debug import edit, find_sus_code

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

def run_test(option: str) -> tbutils.ParsedException:
    os.chdir(PATH_TO_QUIX_REPO)
    command = ["pytest", f"python_testcases/test_{option}.py", "--tb=native"]
    print("Running test: ", " ".join(command))
    stdout = subprocess.run(command, capture_output=True).stdout.decode("utf-8")

    stacktrace = parse_first_stacktrace(stdout)
    return stacktrace

def main():
    # We keep an unchanging folder, static_python_programs, and always create a temporary python_programs directory to be edited
    python_programs_path = PATH_TO_QUIX_REPO + "/python_programs"
    shutil.rmtree(python_programs_path, ignore_errors=True)
    shutil.copytree(PATH_TO_QUIX_REPO + "/static_python_programs", python_programs_path)
    
    outcomes = {}
    for option in list_options():
        # Timeout after 10s
        

        stacktrace = run_test(option)
        filepath = f"{PATH_TO_QUIX_REPO}/python_programs/{option}.py"
        print("Stacktrace: ", stacktrace)
        code_snippets = find_sus_code({
            "stacktrace": stacktrace,
            "code": {
                filepath: open(filepath, "r").read(),
            },
        })
        print("Code snippets: ", code_snippets)
        edited_code = edit({
            "stacktrace": stacktrace,
            "code": code_snippets,
        })
        print("Edited code: ", edited_code)

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