import atheris
import sys

def find_bad_inputs(func: callable, num: int=10, test_func=None) -> list:
    bad_inputs = set()
    atheris.instrument_func(func)

    def TestOneInput(data):
        fdp = atheris.FuzzedDataProvider(data)
        inp = fdp.ConsumeIntListInRange(2, -100, 100)

        try:
            func(inp[0], inp[1])
            if test_func is not None:
                assert test_func(inp[0], inp[1]) == func(inp[0], inp[1])

        except Exception:
            bad_inputs.add((inp[0], inp[1]))

            if len(bad_inputs) > num:
                print("Found bad inputs: ", bad_inputs)
                raise Exception

    atheris.Setup(sys.argv, TestOneInput, enable_python_coverage=True)
    try: atheris.Fuzz()
    except: return bad_inputs

def f(a, b):
    if a < b: return a
    if a - b < 3: raise Exception
    return b

if __name__ == "__main__":
    assert 1 == 2
    find_bad_inputs(f)