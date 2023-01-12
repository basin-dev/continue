import subprocess
from typing import Dict, Tuple
import typer
from debugger import fault_loc
from boltons import tbutils
from llm import OpenAI
from prompts import SimplePrompter, EditPrompter
import ast
import os

llm = OpenAI()
app = typer.Typer()

prompt = '''I ran into this problem with my Python code:

{traceback}

Instructions to fix:

'''
fix_suggestion_prompter = SimplePrompter(lambda stderr: prompt.replace("{traceback}", stderr))

def suggest_fix(stderr: str) -> str:
    full_output = stderr
    
    exc = tbutils.ParsedException.from_string(stderr)
    sus_frame = fault_loc.fl1(exc)
    relevant_frames = fault_loc.filter_relevant(exc.frames)
    exc.frames = relevant_frames

    resp = fix_suggestion_prompter.complete(stderr)

    full_output += "You might be able to fix this problem by following these steps:\n"

    full_output += resp + "\n\n"

    full_output += "If this did not solve the issue, then try running me again for a different suggestion."

    print(full_output)
    return full_output

def compile_edit_prompt(inp: Tuple[Dict, str]) -> str:
    sus_frame, st = inp
    return ast.unparse(fault_loc.get_context(sus_frame)), f"""
    Edit this function to fix the problem shown below in the stack trace:
    {st}"""

make_edit_prompter = EditPrompter(compile_edit_prompt)

def make_edit(stderr: str):
    exc = tbutils.ParsedException.from_string(stderr)
    sus_frame = fault_loc.fl1(exc)
    resp = make_edit_prompter.complete((sus_frame, exc.to_string()))
    with open(sus_frame['filepath'], 'r') as f:
        code = f.read()

    tree = ast.parse(code)
    sus_node = fault_loc.get_context(sus_frame)
    sus_node.body = ast.parse(resp).body

    path, file = os.path.split(sus_frame['filepath'])
    edited_file = os.join(path, "edited_" + file)
    with open(edited_file, 'w') as f:
        f.write(ast.unparse(tree))

    return edited_file

def capture_stderr(filepath: str) -> str | None:
    """Run a Python file and capture the stderr output."""
    proc = subprocess.run(["python", filepath], stderr=subprocess.PIPE)
    stderr = proc.stderr.decode("utf-8")
    print(stderr)
    return stderr

@app.command()
def run(filepath: str):
    stderr = capture_stderr(filepath)
    if stderr == "":
        print("No errors found!")
        return
    suggest_fix(stderr)
    
    edited_file = make_edit(stderr)
    stderr = capture_stderr(edited_file)
    if stderr == "":
        print("Successfully fixed error!")

if __name__ == "__main__":
    app()