import subprocess
from typing import Dict, List, Tuple
from fastapi import APIRouter, Body, Query
from pydantic import BaseModel
import fault_loc
from boltons import tbutils
from llm import OpenAI
from prompts import SimplePrompter, EditPrompter
import ast
import os

llm = OpenAI()
router = APIRouter(prefix="/debug", tags=["debug"])

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

def get_steps(stacktrace: str) -> str:
    exc = parse_stacktrace(stacktrace)
    if len(exc.frames) == 0:
        raise Exception("No frames found in stacktrace")
    sus_frame = fault_loc.fl1(exc)
    relevant_frames = fault_loc.filter_relevant(exc.frames)
    exc.frames = relevant_frames

    resp = fix_suggestion_prompter.complete(stacktrace)
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

@router.post("/run") # This isn't really being used
def run(filepath: str, make_edit: bool = False):
    """Returns boolean indicating whether error was found, edited, and solved, or not all of these."""
    stderr = python_run(filepath)
    if stderr == "":
        return False
        
    steps = suggest_fix(stderr)
    
    if make_edit:
        edited_file = make_edit(stderr, steps)
        stderr = python_run(edited_file)
        if stderr == "":
            return True

class InlineCode(BaseModel):
    filecontents: str
    startline: int
    endline: int
    stacktrace: str = ""

@router.post("/inline")
def inline(body: InlineCode):
    code = fault_loc.find_code_in_range(body.filecontents, body.startline, body.endline)
    suggestion = attempt_edit_prompter1.complete((code, body.stacktrace))
    return {"completion": suggestion}

@router.get("/suggestion")
def suggestion(stacktrace: str):
    suggestion = get_steps(stacktrace)
    return {"completion": suggestion}
 
def ctx_prompt(ctx, final_instruction: str) -> str:
    prompt = ''
    if ctx[0] is not None and ctx[0] != '':
        prompt += f"I ran into this problem with my Python code:\n\n{ctx[0]}\n\n"
    if ctx[1] is not None and len(ctx[1]) > 0:
        prompt += "This is the code I am trying to fix:\n\n"
        i = 1
        for code in ctx[1]:
            if code.strip() != "":
                prompt += f"File #{i}\n```\n{code}\n```\n\n"
                i += 1
    if ctx[2] is not None and ctx[2] != '':
        prompt += f"This is a description of the problem:\n\n{ctx[2]}\n\n"
    
    prompt += final_instruction + "\n\n"
    return prompt

ten_things_prompter = SimplePrompter(lambda ctx: ctx_prompt(ctx, "Here are 10 things I could try to fix the problem:"))

class DebugContext(BaseModel):
    stacktrace: str
    code: List[str]
    description: str

@router.post("/list")
def listten(ctx: DebugContext):
    ten_things = ten_things_prompter.complete((ctx.stacktrace, ctx.code, ctx.description))
    return {"completion": ten_things}

edit_prompter = SimplePrompter(lambda ctx: ctx_prompt(ctx, "This is what the code should be in order to avoid the problem:"))

@router.post("/edit")
def edit(ctx: DebugContext):
    print(edit_prompter._compile_prompt((ctx.stacktrace, ctx.code, ctx.description)))
    new_code = edit_prompter.complete((ctx.stacktrace, ctx.code, ctx.description))
    return {"completion": new_code}

@router.get("/find")
def find_sus_code(stacktrace: str, description: str=None):
    parsed = parse_stacktrace(stacktrace)
    if description is None or description == "":
        description = parsed.exc_type + ": " + parsed.exc_msg

    most_sus_frames = fault_loc.fl2(parsed, description)

    return {"response": [
        fault_loc.frame_to_code_location(frame)
        for frame in most_sus_frames
    ]}