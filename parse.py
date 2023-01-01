import ast
import docstring_parser

def const_signature(const: ast.Constant) -> str:
    if type(const.value) is str:
        return const.value
    elif const.value is None:
        return "None"
    elif const.value.__class__.__name__ == "ellipsis":
        return "..."
    else:
        if type(const.value.__name__) is str:
            return const.value.__name__
        else:
            return "???"

def type_signature(returns: ast.AST) -> str:
    """Get the signature of a return statement."""
    if isinstance(returns, ast.Subscript):
        return f"{returns.value.id}[{type_signature(returns.slice)}]"
    elif isinstance(returns, ast.Name):
        return returns.id
    elif isinstance(returns, ast.List):
        return f"[{', '.join( [type_signature(el) for el in returns.elts] )}]"
    elif isinstance(returns, ast.Tuple):
        return f"({', '.join([type_signature(el) for el in returns.elts])})"
    elif isinstance(returns, ast.Constant):
        return const_signature(returns)
    elif isinstance(returns, ast.Attribute):
        return f"{returns.value.id}.{returns.attr}"
    else:
        raise Exception(f"Unknown return type: {returns} {type(returns)} {returns.__dict__}")

def fn_signature(fn: ast.FunctionDef) -> str:
    """Get the signature of a function. Check for literal type annotations first, then docstring annotations."""

    docstring = ast.get_docstring(fn)
    parsed_ds = docstring_parser.parse(ast.get_docstring(fn))
    ds_args = {}
    ds_return = None
    for meta in parsed_ds.meta:
        if isinstance(meta, docstring_parser.common.DocstringReturns):
            ds_return = meta.type_name
        elif isinstance(meta, docstring_parser.common.DocstringParam):
            ds_args[meta.arg_name] = meta.type_name
        else:
            print("Unknown meta type: ", type(meta))
    
    def arg_signature(arg: ast.arg) -> str:
        """Get the signature of an argument."""
        if arg.annotation is not None:
            return f"{arg.arg}: {type_signature(arg.annotation)}"
        elif arg.arg in ds_args:
            return f"{arg.arg}: {ds_args[arg.arg]}"
        else:
            return arg.arg
    
    sig = f"fn {fn.name}({', '.join([arg_signature(arg) for arg in fn.args.args])})"
    if fn.returns is not None:
        sig += f" -> {type_signature(fn.returns)}"
    elif ds_return is not None:
        sig += f" -> {ds_return}"

    if docstring is not None:
        sig = f'"""{docstring}"""\n' + sig
    
    return sig

def class_signature(cls: ast.ClassDef) -> str:
    """Get the signature of a class."""
    sig = f"class {cls.name}"
    if cls.bases is not None and False: #Giving an error, leaving for now
        sig += f"({', '.join([base.id for base in cls.bases])})"
    
    return sig

def get_signatures(node: ast.AST) -> list[str]:
    """Get the signatures of all top-level functions and classes in a file."""
    signatures = []
    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.FunctionDef):
            sig = str(child)
            try:
                sig = fn_signature(child)
            except Exception as e:
                print("Failed to parse function signature: ", child.name, e)
            signatures.append(fn_signature(child))
        elif isinstance(child, ast.ClassDef):
            signatures.append(class_signature(child))
    
    return signatures

def parse_text(text: str):
    """Parse a string of Python code."""
    return ast.parse(text)