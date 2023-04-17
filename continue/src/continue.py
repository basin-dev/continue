from typer import Typer
from .server.main import app as server_app
import uvicorn

cli_app = Typer()


@cli_app.command()
def start():
    uvicorn.run(server_app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    cli_app()
