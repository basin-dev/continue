import ast
import docstring_parser
from ds_gen import write_ds_for_fn, write_ds_for_class

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
        return f"{type_signature(returns.value)}[{type_signature(returns.slice)}]"
    elif isinstance(returns, ast.Name):
        return returns.id
    elif isinstance(returns, ast.List):
        return f"[{', '.join( [type_signature(el) for el in returns.elts] )}]"
    elif isinstance(returns, ast.Tuple):
        return f"({', '.join([type_signature(el) for el in returns.elts])})"
    elif isinstance(returns, ast.Constant):
        return const_signature(returns)
    elif isinstance(returns, ast.Attribute):
        return f"{type_signature(returns.value)}.{returns.attr}"
    elif isinstance(returns, ast.BinOp) and isinstance(returns.op, ast.BitOr):
        return f"{type_signature(returns.left)} | {type_signature(returns.right)}"
    elif isinstance(returns, ast.Call):
        return f"{type_signature(returns.func)}({', '.join([type_signature(arg) for arg in returns.args])})"
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
    
    sig = f"def {fn.name}({', '.join([arg_signature(arg) for arg in fn.args.args])})"
    if fn.returns is not None:
        sig += f" -> {type_signature(fn.returns)}"
    elif ds_return is not None:
        sig += f" -> {ds_return}"

    if docstring is not None:
        sig = f'"""{docstring}"""\n' + sig
    else:
        # Generate a docstring
        pass
        # ds = write_ds_for_fn(fn)
        # if ds is not None:
        #     ds = ds.split('"""')[1].split('"""')[0].strip()
        #     sig = f'"""{ds}"""\n' + sig
    
    return sig

def class_signature(cls: ast.ClassDef) -> str:
    """Get the signature of a class."""
    sig = f"class {cls.name}"

    # Base classes
    if cls.bases is not None and len(cls.bases) > 0:
        sig += f"({', '.join([type_signature(base) for base in cls.bases])})"

    sig += ":\n"

    # Docstring
    docstring = ast.get_docstring(cls)
    if docstring is not None and len(docstring) > 0:
        sig = f'"""{docstring}"""\n' + sig
    else:
        # Generate a docstring
        pass
        # ds = write_ds_for_class(cls)
        # if ds is not None:
        #     ds = ds.split('"""')[1].split('"""')[0].strip()
        #     sig = f'"""{ds}"""\n' + sig
    
    # Body - condense functions, keep assignments, ignore everything else
    for child in cls.body:
        if isinstance(child, ast.FunctionDef):
            # print(ast.unparse(child))
            fn_sig = fn_signature(child)
            sig += "\t" + "\n\t".join(fn_sig.splitlines()) + "\n"
        elif isinstance(child, ast.Assign) or isinstance(child, ast.AnnAssign):
            sig += "\t" + ast.unparse(child).strip() + "\n"
        else:
            pass
    
    return sig

def get_signatures(node: ast.AST) -> list[str]:
    """Get the signatures of all top-level functions and classes in a file.
    Also includes docstring generation."""
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


def compile_prompt(code: str, file_name: str) -> str:
    """Compile a prompt from a file."""
    prompt = f"\n\n### {file_name} ###\n\n{code}"

    # Now compress into function signatures
    try:
        ass_tree = parse_text(prompt)
        sigs = get_signatures(ass_tree)
        if len(sigs) == 0:
            return None
    except:
        print("Failed to parse.")
        return None

    prompt = "\n\n".join(sigs)
    prompt += "\n\n### Unit tests for the above files using pytest. Make sure they are concise and complete. ###\n\n"
    return prompt