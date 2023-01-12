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
    with open(frame['filename'], "r") as f:
        code = f.read()
    
    return ast.parse(code)

def get_context(frame: Dict) -> str:
    """Get the surrounding context of a frame."""
    tree = parse_frame(frame)
    lineno = frame['lineno']

    # Get the most specific function node containing the line
    best_node = None
    best_dist = float("inf")
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.lineno <= lineno <= node.end_lineno:
            if node.end_lineno - node.lineno < best_dist:
                best_dist = node.end_lineno - node.lineno
                best_node = node

    assert best_node is not None, "No node found that matches lineno"

    return ast.unparse(best_node)


    