import requests

def gh_raw(repo: str, path: str):
    """Get the raw text of a file from GitHub. Try both master and main branches."""
    url = "https://raw.githubusercontent.com/" + repo + "/main/" + path
    response = requests.get(url)
    return response.text

def find_import_dependencies(content: str):
    """Find the imports in a file."""
    imports = []
    for line in content.splitlines():
        if line.startswith("import "):
            imports.append(line.split(" ")[1])
        elif line.startswith("from "):
            imports.append(line.split(" ")[1])
    return imports

def dependency_paths(path: str, dependencies: list[str]):
    """Download the imports in a file."""
    cwd = "/".join(path.split("/")[:-1])
    paths_to_download = set()
    
    for import_ in dependencies:
        if import_.startswith("."):
            # Relative imports
            import_ = import_.replace(".", "")
        paths_to_download.add(cwd + "/" + import_ + ".py")
    
    return paths_to_download