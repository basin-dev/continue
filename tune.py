import json
import os

if __name__ == "__main__":
    # Write the edited tests into the completions file
    completions = json.load(open("completions.json", "r"))

    for test in os.listdir("tests"):
        code_to_test = open("code/" + test, "r").read()
        completions.append({
            "prompt": code_to_test,
            "completion": open("tests/" + test, "r").read().replace(code_to_test, "")
        })

    json.dump(completions, open("completions.json", "w"))