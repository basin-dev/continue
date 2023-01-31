import subprocess
from typing import Dict, List, Any
from textwrap import dedent

def find_sources_in_frame_query(frame: Dict, var_name: str) -> str:
    """Return a CodeQL query that finds sources in a given frame for the given variable name"""
    # Use dedent to make the query more readable
    # query = dedent("""
    #     import python
    #     from DataFlow::PathGraph

    #     class MySource extends DataFlow::Node {
    #         MySource() { this = DataFlow::localSource(DataFlow::TypeTracker::end()) }
    #     }

    #     class MySink extends DataFlow::Node {
    #         MySink() { this = DataFlow::localFlowStep(DataFlow::TypeTracker::end(), MySource()) }
    #     }

    #     from MySource, MySink
    #     select MySource, MySink
    # """)

    return dedent(f"""
        import python
        import semmle.python.dataflow.new.DataFlow

        from DataFlow::MethodCallNode mc, DataFlow::Node mco, DataFlow::Scope src
        where
            mc.getLocation().getFile().getBaseName().matches("{frame['filename']}") and // just restricting the file to be queried
            mco = mc.getObject() and
            mco instanceof DataFlow::MethodCallNode and
            src = mc.getScope()
        select mco, mc, src
    """)


def execute_codeql_query(query: str) -> List[Dict]:
    """Execute a CodeQL query and return the results as a list of dictionaries"""
    # Call the CodeQL CLI to execute the query
    results = subprocess.run(["codeql", "query", "run", "--format=csv", "--no-header", "--no-sarif", "--output=-", "--database=codeql-database", "--search-path=codeql/python/ql/src", "--search-path=codeql/python/ql/src/semmle/python/dataflow/new"], input=query, capture_output=True, text=True)

    # Parse the results into a list of dictionaries
    parsed_results = []
    for line in results.stdout.splitlines():
        parsed_results.append(dict(zip(["mco", "mc", "src"], line.split(","))))

    return parsed_results

def select_single_source(results: List[Dict]) -> Dict:
    """Select a single source from the results of a CodeQL query"""
    # Select the first source for now
    return results[0]

def find_important_lines(frames: List[Dict], var_name: str):
    for frame in frames:
        # Get the sources of the variable from the current frame
        query = find_sources_in_frame_query(frame, var_name)
        results = execute_codeql_query(query)

        # Select a single one of the sources
        source = select_single_source(results)

        # Determine which argument to the function call is the source
        
        # Search the next frame up for a call to the current function
        