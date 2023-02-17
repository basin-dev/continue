import subprocess
from typing import Dict, List
from fastapi import APIRouter
from pydantic import BaseModel
import fault_loc_utils as fault_loc
from boltons import tbutils
from llm import OpenAI
from prompts import SimplePrompter
import ast
import os
from models import RangeInFile, SerializedVirtualFileSystem, Traceback, FileEdit
from virtual_filesystem import VirtualFileSystem, FileSystem
from util import merge_ranges_in_files

llm = OpenAI()
router = APIRouter(prefix="/debug", tags=["debug"])

prompt = '''I ran into this problem with my Python code:

{traceback}

Instructions to fix:

'''
fix_suggestion_prompter = SimplePrompter(lambda stderr: prompt.replace("{traceback}", stderr))


def parse_traceback(stderr: str) -> Traceback:
    # Sometimes paths are not quoted, but they need to be
    if "File \"" not in stderr:
        stderr = stderr.replace("File ", "File \"").replace(", line ", "\", line ")
    tbutil_parsed_exc = tbutils.ParsedException.from_string(stderr)
    return Traceback.from_tbutil_parsed_exc(tbutil_parsed_exc)

def get_steps(traceback: str) -> str:
    traceback = parse_traceback(traceback)
    if len(traceback.frames) == 0:
        raise Exception("No frames found in traceback")
    sus_frame = fault_loc.fl1(traceback)
    relevant_frames = fault_loc.filter_ignored_traceback_frames(traceback.frames)
    traceback.frames = relevant_frames

    resp = fix_suggestion_prompter.complete(traceback)
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
    exc = parse_traceback(stderr)
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

class InlineBody(BaseModel):
    filecontents: str
    startline: int
    endline: int
    traceback: str = ""

@router.post("/inline")
def inline(body: InlineBody):
    code = fault_loc.find_code_in_range(body.filecontents, body.startline, body.endline)
    suggestion = attempt_edit_prompter1.complete((code, body.traceback))
    return {"completion": suggestion}

@router.get("/suggestion")
def suggestion(traceback: str):
    suggestion = get_steps(traceback)
    return {"completion": suggestion}
 
class DebugContextBody(BaseModel):
    traceback: str
    ranges_in_files: List[RangeInFile]
    filesystem: SerializedVirtualFileSystem
    description: str

    def deserialize(self):
        return DebugContext(
            traceback=parse_traceback(self.traceback),
            ranges_in_files=self.ranges_in_files,
            filesystem=VirtualFileSystem(self.filesystem),
            description=self.description
        )

class DebugContext(BaseModel):
    traceback: Traceback
    ranges_in_files: List[RangeInFile]
    filesystem: FileSystem
    description: str

    class Config:
        arbitrary_types_allowed = True

def ctx_prompt(ctx: DebugContext, final_instruction: str) -> str:
    prompt = ''
    if ctx.traceback is not None and ctx.traceback != '':
        prompt += f"I ran into this problem with my Python code:\n\n{ctx.traceback.full_traceback}\n\n"
    if len(ctx.ranges_in_files) > 0:
        prompt += "This is the code I am trying to fix:\n\n"
        i = 1
        for range_in_file in ctx.ranges_in_files:
            contents = ctx.filesystem.read_range_in_file(range_in_file)
            if contents.strip() != "":
                prompt += f"File ({range_in_file.filepath})\n```\n{contents}\n```\n\n"
                i += 1
    if ctx.description is not None and ctx.description != '':
        prompt += f"This is a description of the problem:\n\n{ctx.description}\n\n"
    
    prompt += final_instruction + "\n\n"
    return prompt

n = 3
n_things_prompter = SimplePrompter(lambda ctx: ctx_prompt(ctx, f"List {n} potential solutions to the problem or causes. They should be precise and useful:"))


@router.post("/list")
def listten(body: DebugContextBody):
    n_things = n_things_prompter.complete(body.deserialize())
    return {"completion": n_things}

explain_code_prompter = SimplePrompter(lambda ctx: ctx_prompt(ctx, "Here is a thorough explanation of the purpose and function of the above code:"))

@router.post("/explain")
def explain(body: DebugContextBody):
    explanation = explain_code_prompter.complete(body.deserialize())
    return {"completion": explanation}

edit_prompter = SimplePrompter(lambda ctx: ctx_prompt(ctx, "This is what the code should be in order to avoid the problem:"))

def parse_multiple_file_completion(completion: str, ranges_in_files: List[RangeInFile]) -> Dict[str, str]:
    # Should do a better job of ensuring the ``` format, but for now the issue is mostly just on single file inputs:
    if not '```' in completion:
        completion = "```\n" + completion + "\n```"
    elif completion.splitlines()[0].strip() == '```':
        first_filepath = ranges_in_files[0].filepath
        completion = f"File ({first_filepath})\n" + completion

    suggestions: Dict[str, str] = {}
    current_file_lines: List[str] = []
    current_filepath: str | None = None
    last_was_file = False
    inside_file = False
    for line in completion.splitlines():
        if line.strip().startswith("File ("):
            last_was_file = True
            current_filepath = line.strip()[6:-1]
        elif last_was_file and line.startswith("```"):
            last_was_file = False
            inside_file = True
        elif inside_file:
            if line.startswith("```"):
                inside_file = False
                suggestions[current_filepath] = "\n".join(current_file_lines)
                current_file_lines = []
                current_filepath = None
            else:
                current_file_lines.append(line)
    return suggestions

def suggest_file_edits(ctx: DebugContext) -> List[FileEdit]:
    """Suggest edits in the code to fix the problem."""
    completion = edit_prompter.complete(ctx)
    suggestions = parse_multiple_file_completion(completion, ctx.ranges_in_files)

    edits: List[FileEdit] = []
    for suggestion_filepath, suggestion in suggestions.items():
        range_in_file = list(filter(lambda r: r.filepath == suggestion_filepath, ctx.ranges_in_files))[0]
        edits.append(FileEdit(range=range_in_file.range, filepath=range_in_file.filepath, replacement=suggestion))

    return edits

class EditResp(BaseModel):
    completion: List[FileEdit]

@router.post("/edit")
def edit_endpoint(body: DebugContextBody) -> EditResp:
    edits = suggest_file_edits(body.deserialize())

    return {"completion": edits}

class FindBody(BaseModel):
    traceback: str
    filesystem: SerializedVirtualFileSystem
    description: str | None = None

class FindResp(BaseModel):
    response: List[RangeInFile]

def find_sus_code(traceback: Traceback, filesystem: FileSystem, description: str | None) -> FindResp:
    # Refactor this so it's inside of fl2
    if description is None or description == "":
        description = traceback.message

    most_sus_frames = fault_loc.fl2(traceback, description, filesystem=filesystem)
    range_in_files = [
        fault_loc.frame_to_code_range(frame, filesystem=filesystem)
        for frame in most_sus_frames
    ]
    range_in_files = merge_ranges_in_files(range_in_files)

    return FindResp(**{"response": range_in_files})

@router.post("/find")
def find_sus_code_endpoint(body: FindBody) -> FindResp:
    parsed = parse_traceback(body.traceback)
    filesystem = VirtualFileSystem.from_serialized(body.filesystem)
    return find_sus_code(parsed, filesystem, body.description)