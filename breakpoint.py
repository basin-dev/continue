from typing import Dict

def get_variables(loc: Dict, glob: Dict) -> Dict:
    """Get a dictionary of all variables in the current scope, but remove builtin stuff."""
    glob = glob.copy()
    glob.update(loc)

    unwanted = set(["__builtins__", "__doc__", "__name__", "__package__", "__annotations__", "__file__", "__cached__", "__loader__", "__spec__", "get_variables"])
    unwanted.update(dir(__builtins__))

    for key in list(glob.keys()):
        if key in unwanted:
            del glob[key]
    
    return glob

def format_variables(vars: Dict) -> str:
    """Format a dictionary of variables into a string."""
    return "\n".join([f"{key}={value}" for key, value in vars.items()])