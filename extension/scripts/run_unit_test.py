from typer import Typer
import subprocess

app = Typer()

@app.command()
def run_unit_test(file_and_function_specifier: str):
    try:
        stdout = subprocess.run(["pytest", file_and_function_specifier, "--tb=native"], capture_output=True).stdout.decode("utf-8")
        with open("stdout.txt", "w") as f:
            f.write(stdout)
    except Exception as e:
        with open("stdout.txt", "w") as f:
            f.write(str(e))
    print({ "stdout": stdout })

if __name__ == "__main__":
    app()