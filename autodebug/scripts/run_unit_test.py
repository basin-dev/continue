from typer import Typer
import subprocess

app = Typer()

@app.command()
def run_unit_test(file_and_function_specifier: str):
    stdout = subprocess.run(["pytest", file_and_function_specifier, "--tb=native"], capture_output=True).stdout.decode("utf-8")
    print({ "stdout": stdout })

if __name__ == "__main__":
    app()