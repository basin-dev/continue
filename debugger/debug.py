import subprocess
import openai
import typer
import fault_loc
import os
from dotenv import load_dotenv
from boltons import tbutils

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

def complete(prompt: str, **kwargs) -> str:
    defaults = {
        "engine": "text-davinci-003",
        "temperature": 0.9,
        "max_tokens": 150,
        "top_p": 1,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
    }
    return openai.Completion.create(prompt=prompt, **(defaults | kwargs)).choices[0].text

app = typer.Typer()

prompt = '''I ran into this problem with my Python code:

{traceback}

Instructions to fix:

'''

def suggest_fix(stderr):
    
    exc = tbutils.ParsedException.from_string(stderr)
    sus_frame = fault_loc.fl1(exc)
    relevant_frames = fault_loc.filter_relevant(exc.frames)
    exc.frames = relevant_frames

    response = complete(
        prompt.replace("{traceback}", exc.to_string()),
        temperature=0.9,
        max_tokens=150,
    )

    print("You might be able to fix this problem by following these steps:\n")

    print(response.choices[0].text, end="\n\n")

    print("If this did not solve the issue, then try running me again for a different suggestion.")

def capture_stderr(filepath: str) -> str | None:
    """Run a Python file and capture the stderr output."""
    proc = subprocess.run(["python", filepath], stderr=subprocess.PIPE)
    stderr = proc.stderr.decode("utf-8")
    print(stderr)
    return stderr

@app.command()
def run(filepath: str):
    stderr = capture_stderr(filepath)
    if stderr == "":
        return
    suggest_fix(stderr)
    
    # Actually make the fix and see if it runs
    exc = tbutils.ParsedException.from_string(stderr)
    sus_frame = fault_loc.fl1(exc)
    

if __name__ == "__main__":
    app()