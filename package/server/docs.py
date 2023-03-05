import ast
from ..libs.language_models.prompts import FormatStringPrompter
from ..libs.util import parse_traceback
from ..server.utils import CompletionResponse
from ..fault_loc.main import to_be_ignored_spec
from ..libs.virtual_filesystem import FileSystem, VirtualFileSystem, RealFileSystem
from ..fault_loc.static_call_graph import get_fn_def_in_file
from textwrap import dedent

documentation_prompter = FormatStringPrompter(dedent("""\
    I tried to call a function named "{function}", but it failed.
    
    This is my code:
    ```
    {my_code}
    ```

    This is the definition of the "{function}" function:
    ```
    {fn_def}
    ```

    Adapt my code to correctly call {function}:
    """))
def find_docs(traceback: str, filesystem: FileSystem=RealFileSystem()) -> CompletionResponse:
    parsed = parse_traceback(traceback)

    # Check for external code (not ours) at the bottom of stacktrace
    our_code = False
    last_our_code = None
    first_external_code = None
    for frame in parsed.frames:
        if our_code and to_be_ignored_spec.match_file(frame.filepath):
            first_external_code = frame
            break
        else:
            our_code = True
            last_our_code = frame

    if first_external_code is None:
        return {"completion": "Not found"}
    
    fn_def = get_fn_def_in_file(first_external_code.filepath, first_external_code.function)
    if fn_def is None:
        return {"completion": "Not found"}
    

    completion = documentation_prompter.complete({
        "function": first_external_code.function,
        "path": first_external_code.filepath,
        "my_code": last_our_code.code,
        "fn_def": ast.unparse(fn_def)
    })

    return {"completion": completion}