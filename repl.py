import ast
import openai

TEST_PATH = "./dlt_code/tests/test.py"
CODE_PATH = "./dlt_code/utils.py"

NEXT_ACTION = '''Select next action....

(G [Optional Instructions]) Generate a new test from scatch (with optional instructions)
(E [Required Instructions]) Edit this generation based on instructions (open subprocess with vim???)
(N) Go to next function / class method
(A) Accept this test and add it to the file

Selection: '''

def generate_unit_test(func):
  print("Generated unit test:\n")

  prompt = f"""{function}

  # Write multiple Python unit tests using the pytest library for the above function, using parameterizations and doing a proper partitioning of the input space:"""

  response = openai.Completion.create(
      engine="text-davinci-003",
      prompt=prompt,
      temperature=0.7,
      max_tokens=512,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0
  )

  with open(f'''./generated_tests/test_{file["name"]}''', 'a') as output:
      output.write(response['choices'][0]['text'] + "\n\n")

  print("!!!! unit test !!!\n")

def print_func(func):
  print("Function / class method:\n")
  print(func + "\n")

def grab_funcs():
    with open(CODE_PATH, 'r') as file:
      tree = ast.parse(file.read())

    functions = []
    for node in ast.walk(tree):

        if isinstance(node, ast.FunctionDef):
            if hasattr(node, "parent") and isinstance(node.parent, ast.ClassDef):
                continue
            else:
                functions.append(ast.unparse(node))

        if isinstance(node, ast.ClassDef):
            functions.append({'name': node.name, 'methods': []})
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name == "__init__":
                    functions[-1]['init'] = ast.unparse(child)
                else:
                    functions[-1]['methods'].append(ast.unparse(child))
                child.parent = node # ast.walk traverses ClassDef nodes before FunctionsDef nodes

    return functions

def prompt_user():
    return input(NEXT_ACTION)

def intro_prompt():
    print("Welcome to the REPL!")
    print("Type 'exit' to quit.")
    print("Please set TEST_PATH and CODE_PATH in repl.py before running...")

def repl():
  intro_prompt()
  funcs = grab_funcs()
  func_idx = 0
  while True:
    user_input = prompt_user()
    if user_input == "exit":
      break
    elif user_input.startswith("G"):
      print("\nGenerate\n")
      print_func(funcs[func_idx])
      generate_unit_test(funcs[func_idx])
    elif user_input.startswith("E"):
      print("\nEdit\n")
    elif user_input == "N":
      print("\nNext\n")
      func_idx += 1
      func_idx %= len(funcs)
    elif user_input == "A":
      print("\nAccept\n")
    else:
      print("\nInvalid input. Please try again!\n")

if __name__ == "__main__":
  repl()
  print("Goodbye!")