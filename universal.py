# This file contains prompts for the universal NLP VSCode controller I want to make.

from typing import Dict, List, Tuple
from llm import OpenAI
import prompts
from typer import Typer

gpt = OpenAI()
app = Typer()

def params_formatter(example: Tuple[str, str]) -> str:
    return f"""Request:{example[0]}
Parameters: {example[1]}"""

# (action_id, action_description, parameter prompter) - others: keywords to match against, deterministic short-circuiters, make it a class?
actions = [
    ("autodebug.writeUnitTest", "Write a unit test for a function"),
    ("autodebug.writeTerminalCommand", "Execute a command in terminal"),
    ("autodebug.makeSuggestion", "Make an edit to a code file"),
    ("workbench.action.findInFiles", "Find and replace code within a file", prompts.FewShotPrompter(
        instruction="Given the request, specify the parameters for this operation.",
        examples=[
            ("Find all instances of the word 'test' in the codebase", "query: test"),
            ("Find all instances of the word 'test' in the codebase and replace it with 'testing'", "query: test, replace: testing"),
        ],
        # TODO: Add an intermediate prompt if a regex is needed.
        # TODO: Possibly just generate straight into JSON foramt? It's equally simple to this.
        formatter=params_formatter,
        model="text-davinci-003"
    )),
    ("autodebug.askQuestion", "Answer a question about the codebase"),
    ("autodebug.listTen", "List possible explanations for an error"),
]

def list_actions(actions: List[Tuple[str, str]]) -> str:
    return "\n".join([
            f'- "{action[0]}": {action[1]}'
        for action in actions])

universal_prompt_string = f"""You have the following actions available to you in the format of "{list_actions([("action_id", "action_name")]).replace("- ", "")}":
{list_actions(actions)}

This is the command:

"{{command}}"

State the action_id of the above action needed to complete the command:

"""

# This could almost certainly be done with a fine-tuned curie or pattern-matching to speed things up
univeral_prompter = prompts.SimplePrompter(lambda cmd: universal_prompt_string.format(command=cmd), model="text-davinci-003")

def determineAction(id_resp: str) -> str:
    for action in actions:
        if action[0] in id_resp:
            return action[0]

def get_params(command: str, action: str) -> Dict[str, str]:
    for act in actions:
        if act[0] == action:
            completion = act[2].complete(command)
            try:
                elements = completion.split(",")
                params = { element.split(":")[0].strip() : element.split(":")[1].strip() for element in elements }
                return params
            except:
                return {}

def dict_to_json(d: Dict[str, str]) -> str:
    return "{" + ", ".join([ f'"{key}": "{value}"' for key, value in d.items() ]) + "}"

@app.command()
def main(command: str) -> Tuple[str, Dict[str, str]]:
    id_resp = univeral_prompter.complete(command)
    action = determineAction(id_resp)
    params = get_params(command, action)
    print("Action=" + action)
    print("Params=" + dict_to_json(params))

if __name__ == "__main__":
    app()

# TODO: Need to format arguments in an ordered way probably, but this can happen in typescript