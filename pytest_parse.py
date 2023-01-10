from typing import Any, List, Tuple
import subprocess
import pytest

def parse_collection_tree(test_file_path: str) -> Any:
    """Converts the pytest collection tree into a dictionary representing the tree. For example:
    <Module CWD/pythoncollection.py>
        <Function test_function>
        <Class TestClass>
            <Function test_method>
            <Function test_anothermethod>

    converts to {"Module CWD/pythoncollection.py": {"Function test_function": {}, "Class TestClass": {"Function test_method": {}, "Function test_anothermethod": {}}}
    
    See here: https://docs.pytest.org/en/7.1.x/example/pythoncollection.html#finding-out-what-is-collected
    """
    proc = subprocess.run(["pytest", test_file_path, "--collect-only"], capture_output=True)
    stdout = proc.stdout.decode("utf-8")

    root = {}
    path = [root]
    tab_size = 2
    current_indentation = -2
    for line in stdout.splitlines():
        if line.strip().startswith("<"):
            indentation = len(line.split("<")[0])
            node_key = line.strip()[1:-1] # Get rid of spaces and <>
            if indentation == current_indentation + tab_size:
                # Child of previous
                path[-1][node_key] = {}
                path.append(path[-1][node_key])
            elif indentation == current_indentation:
                # Same level, add to parent (-2 is parent, set this node as last in path instead of path[-1])
                path[-2][node_key] = {}
                path[-1] = path[-2][node_key]
            elif indentation < current_indentation:
                levels_up = (current_indentation - indentation) // tab_size
                for _ in range(levels_up):
                    path.pop()
                path[-2][node_key] = {}
            else:
                raise IndentationError("Invalid indentation in pytest collection tree")
            
            current_indentation = indentation
    
    return root

def get_test_fns(tree: str) -> List[str]:
    """Get all test functions in the file, assuming a single file."""
    test_fns = []
    for line in tree.splitlines():
        if line.strip().startswith("<Function"):
            test_fns.append(line.strip()[1:-1])
    return test_fns

def get_test_statuses(test_file_path: str) -> str:
    """Parse the test status from the pytest output. Assumes only one test is run."""
    stdout = subprocess.run(["pytest", test_file_path, "--tb=no"], capture_output=True).stdout.decode("utf-8")
    lines = list(filter(lambda x: x.endswith("%]"), stdout.splitlines()))
    if len(lines) != 1:
        raise Exception("Wrong number of tests found")
    
    return lines[0].split()[1]

def get_test_coverage(test_file_path: str, code_file_path: str):
    res = pytest.main([test_file_path, "--cov", code_file_path])
    res = pytest.main(["dlt_code/tests/test_small_utils.py", "--cov", "dlt_code/small_utils.py"])
    proc = subprocess.run(["coverage", "run", f"--source={code_file_path}", "-m", "pytest", "-v", test_file_path, "&&", "coverage", "report", "-m"])