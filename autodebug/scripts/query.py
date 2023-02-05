import subprocess
import sys
from gpt_index import GPTSimpleVectorIndex


def query_codebase_index(query):
    """Query the codebase index."""
    branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode("utf-8").strip()
    index = GPTSimpleVectorIndex.load_from_disk('data/{branch}/index.json')
    response = index.query(query)
    print(response)


def query_additional_index(query: str):
    """Query the additional index."""
    index = GPTSimpleVectorIndex.load_from_disk('data/additional_index.json')
    response = index.query(query)
    print(response)


if __name__ == '__main__':
    """python3 query.py <context> <query>"""
    context = sys.argv[1] if len(sys.argv) > 1 else None
    query = sys.argv[2] if len(sys.argv) > 2 else None

    if context == 'additional':
        query_additional_index(query)
    elif context == 'codebase':
        query_codebase_index(query)
    else:
        print('Error: unknown context')