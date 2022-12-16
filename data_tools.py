import requests

def gh_raw(repo: str, path: str):
    """Get the raw text of a file from GitHub. Try both master and main branches."""
    url = "https://raw.githubusercontent.com/" + repo + "/main/" + path
    response = requests.get(url)
    if response.status_code == 404:
        url = "https://raw.githubusercontent.com/" + repo + "/master/" + path
        response = requests.get(url)
    return response

def find_import_dependencies(content: str):
    """Find the imports in a file."""
    imports = []
    for line in content.splitlines():
        if line.startswith("import "):
            imports.append(line.split(" ")[1])
        elif line.startswith("from "):
            imports.append(line.split(" ")[1])
    return imports

def dependency_paths(path: str, dependencies: list[str], repo: str):
    """Download the imports in a file."""
    cwd = "/".join(path.split("/")[:-1])
    paths_to_download = set()

    for import_ in dependencies:
        # Common libraries don't need to be copied: GPT-3 knows about them
        if import_.startswith("."):
            # Relative imports
            import_ = import_[1:].replace(".", "/")
            paths_to_download.add(cwd + "/" + import_ + ".py")
        else:
            # Absolute imports
            if import_.split(".")[0] != repo.split("/")[1]:
                continue

            path = import_.replace(".", "/") + ".py"
            paths_to_download.add(path)

    return list(paths_to_download)