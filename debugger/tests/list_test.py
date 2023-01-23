

import pytest

@pytest.fixture
def setup_function():
    func = ast.FunctionDef(
        name="add_two",
        args=ast.arguments(
            args=[ast.arg(arg="x", annotation=None)],
            vararg=None,
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[]
        ),
        body=[
            ast.Expr(
                value=ast.Call(
                    func=ast.Name(id="print", ctx=ast.Load()),
                    args=[ast.BinOp(
                        left=ast.Name(id="x", ctx=ast.Load()),
                        op=ast.Add(),
                        right=ast.Num(n=2)
                    )],
                    keywords=[]
                )
            )
        ],
        decorator_list=[],
        returns=None
    )
    return func

def test_add_two_function_name(setup_function):
    assert setup_function.name == "add_two"

def test_add_two_function_args(setup_function):
    assert setup_function.args.args[0].arg == "x"

def test_add_two_function_body(setup_function):
    assert setup_function.body[0].value.func.id == "print"
    assert setup_function.body[0].value.args[0].op == ast.Add()
    assert setup_function.body[0].value.args[0].right.n == 2

def test_add_two_function_decorator_list(setup_function):
    assert setup_function.decorator_list == []

def test_add_two_function_returns(setup_function):
    assert setup_function.returns == None
