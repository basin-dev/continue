import github
import slack
import os
import yaml


def get_context(config):

    with open(config, "r") as file:
        data = yaml.safe_load(file)

    context = []

    if data['context']:
        for item in data['context']:
            if item.startswith('https://github.com/'):
                context.append(github.get_issue(item))
            elif item.startswith('https://basindev.slack.com/'):
                context.append(slack.get_thread(item))
            elif item.endswith('.txt'):
                with open(item, 'r') as f:
                    context.append(f.read())
            else:
                print('Context not text file, GitHub Issue, or Slack thread')
    else:
        print('No context found')
    
    return context


if __name__ == '__main__':
    context = get_context('config.yaml')
    print(context)