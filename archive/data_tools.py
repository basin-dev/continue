import requests
from transformers import GPT2TokenizerFast

gpt2_tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

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


COMMON_PYTHON_LIBRARIES = ["re", "os", "sys", "pytest", "json", "logging", "datetime", "random", "time", "string", "math", "hashlib", "base64", "collections", "itertools", "functools", "urllib", "xml", "html", "csv", "copy", "subprocess", "smtplib", "threading", "Queue", "ipaddress", "shutil", "operator", "pathlib", "email", "zlib", "zipfile", "tarfile", "socket", "pickle", "tempfile", "pprint", "numbers", "uuid", "heapq", "bisect", "xmlrpc", "http", "imaplib", "asyncio", "aiohttp", "pdb", "webbrowser", "gc", "decimal", "cgi", "sqlite3", "mysql", "psycopg2", "pyodbc", "cx_Oracle", "lxml", "html5lib", "xml.etree", "xml.dom", "xml.sax", "minidom", "xmlschema", "bs4", "requests", "lxml.html", "pytz", "dateutil", "calendar", "json", "numpy", "pandas", "matplotlib", "sklearn", "tensorflow", "keras", "seaborn", "scipy", "sympy", "statsmodels", "patsy", "scikit-learn", "torch", "torchvision", "fastai", "gym", "nltk", "spacy", "gensim", "pygame", "pyglet", "pyaudio", "pyautogui", "opencv-python", "imageio", "pytesseract", "openpyxl", "xlrd", "xlwt", "xlutils", "pdfminer", "pycrypto", "pycryptodome", "pycryptodomex", "cryptography", "pyopenssl", "pyqrcode", "pyotp", "pycountry", "pytzdata", "pygal", "pygeoip", "pygmaps", "pyexcel", "pyexcelerate", "pymongo", "redis", "pycassa", "pyvcf", "pyarrow", "parser", "parsing", "importlib", "typing", "concurrent", "six", "ctypes", "yaml", "attr", "dataclasses", "weakref", "shlex", "_pytest", "secrets", "warnings", "packaging", "enum", "builtins", "pkg_resources", "traceback", "typing", "abc", "env", "_signal", "setuptools", "argparse", "platform", "glob", "textwrap", "inspect", "parse", "responses", "datasets", "unittest", "random", "statistics", "filecmp", "io", "pkgutil", "fsspec", "tests", "types", "cmath", "multidict", "test", "logging", "__main__", "array", "py", "contextlib", "multiprocessing", "json", "doctest", "__future__", "errno", "difflib", "docstring_parser"]


"""
Technically, you should be always checking if it's from the repo, so you need a reliable way to do this.
Python does this how??

"""

missed_imports = set()

def dependency_paths(path: str, dependencies: list[str], repo: str):
    """Download the imports in a file."""
    cwd = "/".join(path.split("/")[:-1])
    paths_to_download = set()

    for import_ in dependencies:
        # Common libraries don't need to be copied: GPT-3 knows about them
        if import_.split(".")[0] in COMMON_PYTHON_LIBRARIES:
            continue

        if import_.startswith("."):
            # Relative imports
            import_ = import_[1:].replace(".", "/")
            paths_to_download.add(cwd + "/" + import_ + ".py")
        elif import_.split(".")[0] == repo.split("/")[1]:
            # Frequently, the import will have the same name as the repo
            path = import_.replace(".", "/") + ".py"
            paths_to_download.add(path)
        else:
            # See if the import is a file in same directory as current file
            path = cwd + "/" + import_.split(".")[-1] + ".py"
            resp = gh_raw(repo, path)
            if resp is None or resp.status_code == 404:
                # print(resp, path.split("/")[-1])
                missed_imports.add(path.split("/")[-1].replace(".py", ""))
                continue
            else:
                paths_to_download.add(path)


    return list(paths_to_download)

def count_tokens(text: str):
    """Count the number of tokens in a string."""
    return len(gpt2_tokenizer.encode(text))
    
price_per_token = {
    "davinci": 0.03,
    "curie": 0.03,
    "babbage": 0.0006,
    "ada": 0.0004,
}