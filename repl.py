import ast
import openai
import os

TEST_PATH = "./dlt_code/tests/test.py"
CODE_PATH = "./dlt_code/utils.py"

NEXT_ACTION = '''Select next action....

(G) Generate a new test from scatch
(N) Go to next function / class method
(A) Accept this test and add it to the file

Selection: '''

def add_unit_test_to_file(unit_test):
  
  if not os.path.exists("./generated_tests"):
      os.makedirs("./generated_tests")

  file = CODE_PATH.split("/")[-1]

  with open(f'''./generated_tests/test_{file}''', 'a') as output:
      output.write(unit_test + "\n\n")

def generate_unit_test(func):

  prompt = f"""{func}

  # Write one Python unit test using the pytest library for the above function, using parameterizations and doing a proper partitioning of the input space:
  """

  response = openai.Completion.create(
      engine="text-davinci-003",
      prompt=prompt,
      temperature=0.7,
      max_tokens=512,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0
  )

  return response.choices[0].text

def print_func(func):
  print("\nCurrent function / class method:\n")
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
  cur_unit_test = None
  while True:
    print_func(funcs[func_idx])
    user_input = prompt_user()
    if user_input == "exit":
      break
    elif user_input.startswith("G"):
      cur_unit_test = generate_unit_test(funcs[func_idx])
      print("Generated unit test:")
      print(cur_unit_test)
    elif user_input == "N":
      func_idx += 1
      func_idx %= len(funcs)
    elif user_input == "A":
      if cur_unit_test is None:
        print("\nNo unit test to add. Please generate one first.\n")
      else:
        add_unit_test_to_file(cur_unit_test)
        print("\nAdded unit test to file.\n")
    else:
      print("\nInvalid input. Please try again!\n")

if __name__ == "__main__":
  repl()
  print("Goodbye!")