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

class Action:
    def __init__(self, id: str, description: str, examples: List[Tuple[str, str]] = []):
        self.id = id
        self.description = description
        self.params_prompter = prompts.FewShotPrompter(
            instruction="Given the request, specify the parameters for this operation.",
            examples=examples,
            # TODO: Add an intermediate prompt if a regex is needed.
            # TODO: Possibly just generate straight into JSON foramt? It's equally simple to this.
            formatter=params_formatter,
            model="text-davinci-003"
        )

    def fake_id(self) -> str:
        # Because in a situation where only one of the commands was formatted as workbench.action.<action_id>, and the others were autodebug.<action_id>, it only selected the former.
        return "workbench.action." + self.id.split(".")[-1]

# (action_id, action_description, parameter prompter) - others: keywords to match against, deterministic short-circuiters, make it a class?
actions = [
    Action("autodebug.writeUnitTest", "Write a unit test for a function"),
    Action("autodebug.inputTerminalCommand", "Execute a command in terminal", [
        ("List the files in the current directory", "command: ls"),
        ("What is the current working directory?", "command: pwd"),
        ("Write integers 1-10 to a file called 'test.txt'", "command: echo {1..10} > test.txt"),
    ]),
    Action("autodebug.makeSuggestion", "Make an edit to a code file"),
    Action("workbench.action.findInFiles", "Find and replace code within a file", [
        ("Find all instances of the word 'test' in the codebase", "query: test"),
        ("Find all instances of the word 'test' in the codebase and replace it with 'testing'", "query: test, replace: testing"),
    ]),
    Action("autodebug.askQuestion", "Answer a question about the codebase"),
    Action("autodebug.listTen", "List possible explanations for an error"),
]

def list_actions(actions: List[Action]) -> str:
    return "\n".join([
            f'- "{action.fake_id()}": {action.description}'
        for action in actions])

universal_prompt_string = f"""You have the following actions available to you in the format of "{list_actions([Action("action_id", "action_description")]).replace("- ", "")}":
{list_actions(actions)}

This is the command:

"{{command}}"

State the action_id of the above action needed to complete the command. You must choose from the above action_ids:

"""

# This could almost certainly be done with a fine-tuned curie or pattern-matching to speed things up
univeral_prompter = prompts.SimplePrompter(lambda cmd: universal_prompt_string.format(command=cmd), model="text-davinci-003")

def determineAction(id_resp: str) -> str:
    for action in actions:
        if action.fake_id() in id_resp:
            return action.id

def get_params(command: str, action: str) -> Dict[str, str]:
    for act in actions:
        if act.id == action:
            completion = act.params_prompter.complete(command)
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
    print(universal_prompt_string.format(command=command))
    id_resp = univeral_prompter.complete(command)
    print(id_resp)
    action = determineAction(id_resp)
    params = get_params(command, action)
    print("Action=" + action)
    print("Params=" + dict_to_json(params))

if __name__ == "__main__":
    app()

# TODO: Need to format arguments in an ordered way probably, but this can happen in typescript