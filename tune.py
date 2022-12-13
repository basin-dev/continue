import json

if __name__ == "__main__":
    # Write the edited tests into the completions file
    code_to_test = open("code_to_test.py", "r").read()
    completions = json.load(open("completions.json", "r"))
    completions.append({
        "prompt": code_to_test,
        "completion": open("naive.py", "r").read().replace(code_to_test, "")
    })

    json.dump(completions, open("completions.json", "w"))