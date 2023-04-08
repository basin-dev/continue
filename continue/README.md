Create a virtual environment:
```
poetry install
```

Activate the virtual environment
```
poetry shell
```

from `/continue` directory

Run the server:
```
uvicorn continue.src.server.main:app
```