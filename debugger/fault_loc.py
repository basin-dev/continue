from typing import Callable, Dict, List, Tuple
from boltons import tbutils
import ast

ignore = ["bin/"] # Ideally just write in .gitignore-style format, and this can be customizable
def is_my_code(path: str) -> bool:
    for p in ignore:
        if path.startswith(p):
            return False

        if not p.startswith("/") and p in path:
            return False
    
    return True

def filter_relevant(frames: List[Dict]) -> List[Dict]:
    """Filter out frames that are not relevant to the user's code."""
    return list(filter(lambda x: is_my_code(x['filepath']), frames))

def fl1(tb: tbutils.ParsedException) -> Dict:
    """Find the most relevant frame in the traceback."""
    relevant = filter_relevant(tb.frames)
    if len(relevant) == 0:
        return tb.frames[-1]
    return relevant[-1]

def parse_frame(frame: Dict) -> ast.AST:
    with open(frame['filepath'], "r") as f:
        code = f.read()
    
    return ast.parse(code)

def is_valid_context(node: ast.AST, lineno: int) -> bool:
    """Check if the node is a valid context for the line number."""
    return (isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef)) and node.lineno <= int(lineno) <= node.end_lineno

def edit_context_ast(frame: Dict, replacement: Callable[[str], str]) -> ast.AST | None:
    """Get the surrounding context of a frame, and edit it, replacing the node in the AST and returning the updated version."""
    tree = parse_frame(frame)
    lineno = int(frame['lineno'])

    # Get the most specific function node containing the line
    for parent in ast.walk(tree):
        i = 0
        for child in ast.iter_child_nodes(parent):
            if is_valid_context(child, lineno):
                if len(list(filter(lambda x: is_valid_context(x, lineno), child.body))) > 0:
                    # More specific context can be found in the body of this function
                    continue

                str_node = ast.unparse(child)
                new_node = ast.parse(replacement(str_node))
                parent.body[i] = new_node
                return tree
            i += 1

    return None

def get_coverage_data(filename):
    """Get the coverage data for a file."""
    import coverage

    cov = coverage.Coverage()

    cov.start()

    import script

    cov.stop()

    return cov.get_data()

def get_program_structure(filename):
    """Get the program structure for a file."""

    with open(filename, "r") as f:
        code = f.read()

    tree = ast.parse(code)

    return ast.walk(tree)

def fault_localization(coverage_data, program_structure):
    """Calculate the suspiciousness of each statement in the program."""
    
    suspiciousness = {}
    
    for statement in program_structure:
        executed = coverage_data[statement]
        
        total = sum(coverage_data.values())
        
        suspiciousness[statement] = 1 - (executed / total)
    
    return suspiciousness

def find_suspcious_lines():
    """Find the suspicious lines in a file."""
    coverage_data = get_coverage_data("script.py")
    program_structure = get_program_structure("script.py")
    suspiciousness = fault_localization(coverage_data, program_structure)

def find_function_calls(node, function_name, function_calls=[]):
    """Find all function calls to a function in an AST."""
    if isinstance(node, ast.Call):

        if hasattr(node.func, 'id') and node.func.id == function_name:

            function_calls.append((node.lineno, ast.get_source_segment(node)))

    for child in ast.iter_child_nodes(node):

        find_function_calls(child, function_name, function_calls)

    return function_calls

def get_function_calls(file_path, function_name):
    """Get all function calls to a function in a file."""
    with open(file_path, 'r') as file:

        root = ast.parse(file.read())

        function_calls = find_function_calls(root, function_name)

        return function_calls