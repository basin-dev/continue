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
    exc = tbutils.ParsedException.from_string(stderr)
    sus_frame = fault_loc.fl1(exc)
    relevant_frames = fault_loc.filter_relevant(exc.frames)
    exc.frames = relevant_frames

    resp = fix_suggestion_prompter.complete(stderr)

    print("You might be able to fix this problem by following these steps:\n")

    print(resp, end="\n\n")

    print("If this did not solve the issue, then try running me again for a different suggestion.")

    return resp

attempt_prompt = '''This was my Python code:

{code}

I ran into this problem with my Python code:

{traceback}

This is my Python code after I fixed the problem:

'''
attempt_edit_prompter1 = SimplePrompter(lambda x: attempt_prompt.replace("{code}", x[0]).replace("{traceback}", x[1]))

attempt_prompt2 = '''This was my Python code:

{code}

I ran into this problem with my Python code:

{traceback}

These are the steps to fix the problem:

{steps}

This is my Python code after I fixed the problem:

'''
attempt_edit_prompter2 = SimplePrompter(lambda x: attempt_prompt.replace("{code}", x[0]).replace("{traceback}", x[1]).replace("{steps}", x[2]))

def make_edit(stderr: str, steps: str):
    # Compile prompt, get response
    exc = tbutils.ParsedException.from_string(stderr)
    sus_frame = fault_loc.fl1(exc)

    new_ast = fault_loc.edit_context_ast(sus_frame, lambda code_to_change: 
        attempt_edit_prompter2.complete((code_to_change, exc.to_string(), steps))
    )

    path, file = os.path.split(sus_frame['filepath'])
    edited_file = os.path.join(path, "edited_" + file)
    with open(edited_file, 'w') as f:
        f.write(ast.unparse(new_ast))

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
    steps = suggest_fix(stderr)
    
    edited_file = make_edit(stderr, steps)
    stderr = capture_stderr(edited_file)
    if stderr == "":
        print("Successfully fixed error!")

if __name__ == "__main__":
    app()