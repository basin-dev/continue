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
    # node.lineno - 1 because lineno starts at the body of the node, not the def or class line
    return (isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef)) and node.lineno - 1 <= int(lineno) <= node.end_lineno

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
                    # More specific context can be found inthe body of this function
                    continue

                str_node = ast.unparse(child)
                new_node = ast.parse(replacement(str_node))
                parent.body[i] = new_node
                return tree
            i += 1

    return None

def find_most_specific_context(tree: ast.AST, lineno: int) -> ast.AST | None:
    # Get the most specific function node containing the line
    for parent in ast.walk(tree):
        i = 0
        for child in ast.iter_child_nodes(parent):
            if is_valid_context(child, lineno):
                if len(list(filter(lambda x: is_valid_context(x, lineno), child.body))) > 0:
                    # More specific context can be found inthe body of this function
                    continue
                
                return child
            i += 1

    return None