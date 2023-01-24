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


def parse_stacktrace(stderr: str) -> tbutils.ParsedException:
    # Sometimes paths are not quoted, but they need to be
    if "File \"" not in stderr:
        stderr = stderr.replace("File ", "File \"").replace(", line ", "\", line ")
    return tbutils.ParsedException.from_string(stderr)

def get_steps(stderr: str) -> str:
    exc = parse_stacktrace(stderr)
    if len(exc.frames) == 0:
        raise Exception("No frames found in stacktrace")
    sus_frame = fault_loc.fl1(exc)
    relevant_frames = fault_loc.filter_relevant(exc.frames)
    exc.frames = relevant_frames

    resp = fix_suggestion_prompter.complete(stderr)
    return resp

def suggest_fix(stderr: str) -> str:
    steps = get_steps(stderr)

    print("You might be able to fix this problem by following these steps:\n")

    print(steps, end="\n\n")

    print("If this did not solve the issue, then try running me again for a different suggestion.")

    return steps

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
    exc = parse_stacktrace(stderr)
    sus_frame = fault_loc.fl1(exc)

    new_ast = fault_loc.edit_context_ast(sus_frame, lambda code_to_change: 
        attempt_edit_prompter2.complete((code_to_change, exc.to_string(), steps))
    )

    path, file = os.path.split(sus_frame['filepath'])
    edited_file = os.path.join(path, "edited_" + file)
    with open(edited_file, 'w') as f:
        f.write(ast.unparse(new_ast))

    return edited_file

def python_run(filepath: str) -> str | None:
    """Run a Python file and capture the stderr output."""
    proc = subprocess.run(["python", filepath], stderr=subprocess.PIPE)
    stderr = proc.stderr.decode("utf-8")
    print(stderr)
    return stderr

@app.command()
def run(filepath: str, make_edit: bool = False):
    stderr = python_run(filepath)
    if stderr == "":
        print("No errors found!")
        return
        
    steps = suggest_fix(stderr)
    
    if make_edit:
        edited_file = make_edit(stderr, steps)
        stderr = python_run(edited_file)
        if stderr == "":
            print("Successfully fixed error!")

@app.command()
def inline(filepath: str, startline: int, endline: int, stacktrace: str):
    code = fault_loc.find_code_in_range(filepath, startline, endline)
    suggestion = attempt_edit_prompter1.complete((code, stacktrace))
    print("Suggestion=", suggestion)

@app.command()
def suggestion(stderr: str):
    suggestion = get_steps(stderr)
    print("Suggestion=", suggestion)

 
def ctx_prompt(ctx, final_instruction: str) -> str:
    prompt = ''
    if ctx[0] is not None and ctx[0] != '':
        prompt += f"I ran into this problem with my Python code:\n\n{ctx[0]}\n\n"
    if ctx[1] is not None and ctx[1] != '':
        prompt += f"This is the code I am trying to fix:\n\n{ctx[1]}\n\n"
    if ctx[2] is not None and ctx[2] != '':
        prompt += f"This is a description of the problem:\n\n{ctx[2]}\n\n"
    
    prompt += final_instruction + "\n\n"
    return prompt

ten_things_prompter = SimplePrompter(lambda ctx: ctx_prompt(ctx, "Here are 10 things I could try to fix the problem:"))

@app.command()
def listten(stacktrace: str, code: str, description: str):
    ten_things = ten_things_prompter.complete((stacktrace, code, description))
    print("Ten Things=", ten_things)

edit_prompter = SimplePrompter(lambda ctx: ctx_prompt(ctx, "This is my code after I fixed the problem:"))

@app.command()
def edit(stacktrace: str, code: str, description: str):
    new_code = edit_prompter.complete((stacktrace, code, description))
    print("Edited Code=", new_code)

if __name__ == "__main__":
    app()