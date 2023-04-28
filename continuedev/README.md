## Steps to start

- `cd continue/continue`
- Make sure packages are installed with `poetry install`
- `poetry shell`
- `cd ..`
- `python3 -m continue.src.continue`

## Steps to generate JSON Schema

Same up until last step and then `python3 -m continue.src.scripts.gen_json_schema`.

## Start the server

Same steps, then `uvicorn continue.src.server.main:app --reload`.
