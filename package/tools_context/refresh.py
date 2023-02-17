import git
import json
import os

from dotenv import load_dotenv
from gpt_index import GPTSimpleVectorIndex, SimpleDirectoryReader

load_dotenv()

# define in .env file
REPO_PATH = os.getenv('REPO_PATH')


def get_latest_commit(repo: git.Repo, branch: str):
    """Get the latest commit of a branch."""
    return repo.commit(branch)


def save_metadata(repo: git.Repo, branch: str):
    """Save the latest commit of a branch to a file."""
    dir = REPO_PATH + f'/autodebug/data/{branch}'
    if not os.path.exists(dir):
        os.makedirs(dir)
    metadata = { 'latest_commit': str(get_latest_commit(repo, branch)) }
    with open(dir + '/metadata.json', 'w') as f:
        json.dump(metadata, f, indent=4)


def create_branch_index(repo: git.Repo, branch: str):
    """Create the index for a branch."""
    dir = REPO_PATH + f'/autodebug/data/{branch}'
    if not os.path.exists(dir):
        os.makedirs(dir)
    documents = SimpleDirectoryReader(REPO_PATH).load_data()
    index = GPTSimpleVectorIndex(documents)
    index.save_to_disk(dir + '/index.json')
    save_metadata(repo, branch)


def check_metadata(repo: git.Repo, branch: str):
    """Check if the latest commit of a branch is the same as the one saved in the file."""
    dir = REPO_PATH + f'/autodebug/data/{branch}'
    if not os.path.exists(dir):
        return False
    with open(dir + '/metadata.json', 'r') as f:
        metadata = json.load(f)
    return metadata['latest_commit'] == str(get_latest_commit(repo, branch))


def get_branch_index(repo: git.Repo, branch: str):
    """Get the index of a branch."""
    dir = REPO_PATH + f'/autodebug/data/{branch}'
    if not os.path.exists(dir):
        create_branch_index(repo, branch)
    return GPTSimpleVectorIndex.load_from_disk(dir + '/index.json')


if __name__ == '__main__':
    """Example usage."""
    repo = git.Repo(REPO_PATH)
    branch = repo.active_branch.name
    index = get_branch_index(repo, branch)
    response = index.query('is this file about the slack API?')
    print(response)