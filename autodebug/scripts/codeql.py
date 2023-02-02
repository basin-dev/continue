import subprocess
from typing import Any, Dict, List
from typer import Typer
import json
import os

app = Typer()

# @app.command()
def analyze(database: str, query: str | List[str]) -> Dict[str, Any]:
    """
    Run a CodeQL query against a database.
    """
    if isinstance(query, str):
        query = [query]

    subprocess.run(
        ["codeql", "database", "analyze", database, *query, "--format=sarif-latest", "--output=out.sarif"],
        check=True
    )

    with open("out.sarif", "r") as f:
        output = json.load(f)

    os.remove("out.sarif")
    return output


# @app.command()
def create_database(src_root: str, dest: str, language: str="python"):
    """
    Create a CodeQL database from a source root.
    """
    codeql_process = subprocess.run(["codeql", "database", "create", dest, "--language=" + language, "--source-root=" + src_root], check=True, capture_output=True)

if __name__ == "__main__":
    app()