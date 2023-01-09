from typing import Dict


def fn_1(fn_code: str) -> str:
    return f"""{fn_code}

# Write multiple Python unit tests using the pytest library for the above function, using parameterizations and doing a proper partitioning of the input space:"""

def fn_2(fn_code: str) -> str:
    return f"""{fn_code}

# Write multiple Python unit tests using the pytest library for the above function, ensuring 100% coverage of the lines:"""

def cls_1(cls_name: str, init: str, method: str) -> str:
    return f"""class {cls_name}:
{init}
{method}

# Write multiple Python unit tests using the pytest library for the above class and its {method.split("def ")[1].split("(")[0]} method, using fixtures and parameterizations and doing a proper partitioning of the input space:"""

