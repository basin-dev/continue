# This file contains prompts to use for generating pytests
# Other ideas:
# Purposefully clean up anything that was created during the test (this can be done deterministically at least for files)
# Edit mode on fixtures or however you make a mock class in pytest

import ast

# Helpers
def cls_method_to_str(cls_name: str, init: str, method: str) -> str:
    """Convert class and method info to formatted code"""
    return f"""class {cls_name}:
{init}
{method}
"""

# Completion mode
def fn_1(fn_code: str) -> str:
    return f"""{fn_code}

# Write multiple Python unit tests using the pytest library for the above function, using parameterizations and doing a proper partitioning of the input space:"""

def fn_2(fn_code: str) -> str:
    return f"""{fn_code}

# Write multiple Python unit tests using the pytest library for the above function, ensuring 100% coverage of the lines:"""

def cls_1(cls_name: str, init: str, method: str) -> str:
    return f"""{cls_method_to_str(cls_name, init, method)}
# Write multiple Python unit tests using the pytest library for the above class and its {method.split("def ")[1].split("(")[0]} method, using fixtures and parameterizations and doing a proper partitioning of the input space:"""


# Edit mode
def fn_edit_check_return(fn_code: str) -> str:
    # This is only if the function has a return
    fn = ast.parse(fn_code).body[0]
    args = ", ".join([arg.arg for arg in fn.args.args])
    test_args = ", ".join(args) + ", expected"
    return f"""{fn_code}

# Write multiple Python unit tests using the pytest library for the above function, using parameterizations and doing a proper partitioning of the input space:
@pytest.mark.parametrize("{test_args}", [
    [INSERT]
])
def test_{fn.name}({test_args}):
    assert {fn.name}({", ".join(args)}) == expected
"""

# Mock a class
def cls_mock(cls_name: str, init: str, method: str) -> str:
    return f"""{cls_method_to_str(cls_name, init, method)}
# Create a mocked version of the above class in order to use with pytest:"""

# Use the mocked class to write tests
def cls_with_mock(cls_name: str, init: str, method: str, mock: str) -> str:
    return f"""{cls_method_to_str(cls_name, init, method)}
    
{mock}

# Use mock version of the {cls_name} class to write pytest tests for the {method} method:"""