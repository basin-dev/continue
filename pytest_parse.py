from typing import Any, List, Tuple
import xml.etree.ElementTree as ET
import subprocess
import pytest
import ast

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

def run_coverage(test_folder_path: str, module_path: str) -> str:
    stdout = pytest.main([test_folder_path, "--cov", module_path, "--cov-report", "xml", "--cov-report", "term-missing"], capture_output=True).stdout
    return str(stdout)

def parse_cov_xml(path: str) -> Tuple[set, set]:
    """Parse coverage.xml to determine which lines of which functions were covered and which not"""
    tree = ET.parse(path)
    root = tree.getroot()

    covered_lines = set()
    uncovered_lines = set()
    for class_ in root.iter("class"):
        if lines := class_.find("lines"):
            for line in lines.iter("line"):
                num = int(line.attrib["number"])
                (covered_lines if line.attrib["hits"] != "0" else uncovered_lines).add(num)

    return covered_lines, uncovered_lines

def uncovered_lines_for_ast(code_file_path: str, ast: ast.AST, uncovered_lines: List[int]) -> List[Tuple[int, str]]:
    """Given file and ast in question, enrich the uncovered lines within the ast with string representations of the line."""
    with open(code_file_path, "r") as f:
        lines = f.readlines()
    
    uncovered_lines_with_str = []
    for line_num in range(ast.lineno, ast.end_lineno + 1):
        uncovered_lines_with_str.append((line_num, lines[line_num - 1])) # -1 because line numbers are 1-indexed
    
    return uncovered_lines_with_str
