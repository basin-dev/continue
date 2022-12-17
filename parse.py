import ast

def arg_signature(arg: ast.arg) -> str:
    """Get the signature of an argument."""
    if arg.annotation is None:
        return arg.arg
    else:
        return f"{arg.arg}: {arg.annotation.id}"

def fn_signature(fn: ast.FunctionDef) -> str:
    """Get the signature of a function."""
    sig = f"fn {fn.name}({', '.join([arg_signature(arg) for arg in fn.args.args])})"
    if fn.returns is not None:
        sig += f" -> {fn.returns.id}"

    docstring = ast.get_docstring(fn)
    if docstring is not None:
        sig = f'"""{docstring}"""\n' + sig
    
    return sig

def class_signature(cls: ast.ClassDef) -> str:
    """Get the signature of a class."""
    sig = f"class {cls.name}"
    if cls.bases is not None:
        sig += f"({', '.join([base.id for base in cls.bases])})"
    
    return sig

def get_signatures(node: ast.AST) -> list[str]:
    """Get the signatures of all top-level functions and classes in a file."""
    signatures = []
    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.FunctionDef):
            signatures.append(fn_signature(child))
        elif isinstance(child, ast.ClassDef):
            signatures.append(class_signature(child))
    
    return signatures