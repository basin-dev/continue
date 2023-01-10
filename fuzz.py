from typing import Any, List
import atheris
import sys

def generate_args(types: List[type], data) -> List[Any]:
    """Given the list of types needed for function arguments, generate them from an atheris.FuzzedDataProvider"""
    fdp = atheris.FuzzedDataProvider(data)
    inp = []

    for t in types:
        if t is int:
            inp.append(fdp.ConsumeInt())
        elif t is str:
            inp.append(fdp.ConsumeString())
        else:
            raise NotImplementedError

    return inp

def find_bad_inputs(func: callable, types: List[type], num: int=10, test_func=None) -> list:
    bad_inputs = set()
    atheris.instrument_func(func)

    def TestOneInput(data):
        inp = generate_args(types, data)

        try:
            output = func(*inp)
            if test_func is not None:
                assert test_func(*inp) == output

        except Exception:
            bad_inputs.add(inp)

            if len(bad_inputs) > num:
                print("Found bad inputs: ", bad_inputs)
                # Once we've found the desired num of unique bad inputs, we raise an Exception in order to exit the atheris runner (atheris.Fuzz() below)
                raise Exception

    atheris.Setup(sys.argv, TestOneInput, enable_python_coverage=True)
    try: atheris.Fuzz()
    except: return bad_inputs