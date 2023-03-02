import trace
from typing import Callable, List
from .utils import find_fn_def_range
from ..libs.virtual_filesystem import FileSystem, VirtualFileSystem, RealFileSystem
from ..libs.models.main import TracebackFrame, CallGraph
import importlib.util
import sys
import os

def sum(a, b):
    return a + b

def main():
    c = sum(1, 2)
    return c

def b():
    return main()

def trace_results(fn: Callable) -> trace.CoverageResults:
    tracer = trace.Trace(count=1, trace=1, countfuncs=1, countcallers=1)
    import __main__
    __main__.__dict__['__test_function__'] = fn
    tracer.run("__test_function__()")
    results = tracer.results()
    return results

def cov_results_to_call_graph(results: trace.CoverageResults, root_filepath: str, root_fn_name: str, filesystem: FileSystem=VirtualFileSystem({})) -> CallGraph:
    root_key = None
    # Convert tuple pairs to dictionary
    callers_to_callees = {}
    for caller, callee in results.callers:
        if caller not in callers_to_callees:
            callers_to_callees[caller] = []
        callers_to_callees[caller].append(callee)

        if root_key is None and caller[0] == root_filepath and caller[2] == root_fn_name:
            root_key = caller
    
    if root_key is None:
        raise Exception("Couldn't find the root function in the reported execution trace. Check that the root_fn_name and root_filepath have been passed correctly.")

    # Helper function for recursion
    seen = set([])
    def key_to_call_graph(caller_key) -> CallGraph:
        # Avoid loops
        if caller_key in seen:
            return None
        seen.add(caller_key)

        # Recurse into each callee (DFS)
        calls = []
        if caller_key in callers_to_callees:
            for callee in callers_to_callees[caller_key]:
                if call := key_to_call_graph(callee):
                    calls.append(call)

        # Put together a CallGraph object
        caller_filepath = caller_key[0]
        caller_name = caller_key[2]
        return CallGraph(
            function_name=caller_name,
            function_range=find_fn_def_range(caller_filepath, caller_name, filesystem),
            calls=calls
        )

    # Construct graph rooted in fn_name
    return key_to_call_graph(root_key)

def prune_call_graph(call_graph: CallGraph) -> CallGraph:
    return call_graph

def trace_unit_test(test_fn_name: str, test_filepath) -> trace.CoverageResults:
    module_name = os.path.basename(test_filepath).split('.')[0]
    spec = importlib.util.spec_from_file_location(module_name, test_filepath)
    new_module_name = "python.tests." + module_name
    spec.name = new_module_name
    spec.loader.name = new_module_name
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(test_filepath), '..'))
    sys.path.append(parent_dir)
    module = importlib.util.module_from_spec(spec)
    sys.modules[new_module_name] = module
    spec.loader.exec_module(module)

    test_fn = module.__dict__[test_fn_name]

    return trace_results(test_fn)

if __name__ == "__main__":
    test_filepath = "/Users/natesesti/Desktop/basin/unit-test-experiments/extension/examples/python/tests/test_sum.py"
    test_fn_name = "test_sum"

    cov_results = trace_unit_test(test_fn_name, test_filepath)

    cg = cov_results_to_call_graph(cov_results, test_filepath, test_fn_name, filesystem=RealFileSystem())
    print(cg.__dict__)