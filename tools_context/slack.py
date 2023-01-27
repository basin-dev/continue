
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('SLACK_API_TOKEN')

def get_thread(link):

    # Slack API endpoint for conversations.history
    url = "https://slack.com/api/conversations.history"

    # get the conversation id from the link
    conversation_id = link.split("/")[-1]

    # parameters for the API request
    params = {
        "token": token,
        "channel": conversation_id
    }

    # make the API request
    response = requests.get(url, params=params)

    if response.status_code == 200:
        print(response.text)
        replies = json.loads(response.text)["messages"]
        return replies
    else:
        print("Error : {}".format(response.text))
        return