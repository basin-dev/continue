import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('GITHUB_API_TOKEN')
owner = 'basin-dev'
repo = 'unit-test-experiments'

def get_issues(owner, repo, token):

    url = f'https://api.github.com/repos/{owner}/{repo}/issues'

    headers = {'Authorization': 'Token ' + token}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        issues = response.json()
        with open('data/issues.json', 'w') as f:
            json.dump(issues, f, indent=4)
    else:
        print('Failed to retrieve issues')

    # for issue in issues:
    #    print('GitHub Repository: ' + owner + '/' + repo)
    #    print('GitHub Issue: #' + str(issue['number']) + ' ' + issue['title'])
    #    if issue['body']:
    #        print('Description: ', issue['body'])

def get_issue(link):

    owner, repo, feature, num = link.split("/")[-4:]

    if feature != 'issues':
        print("Not a valid GitHub issue link")
        return

    url = f'https://api.github.com/repos/{owner}/{repo}/issues/{num}'

    headers = {'Authorization': 'Token ' + token}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        issue = response.json()
        return issue
    else:
        print('Failed to retrieve issue')
        return

if __name__ == '__main__':
    get_issues(owner, repo, token)