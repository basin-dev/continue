from textwrap import dedent
from typing import Coroutine
from ...models.main import Range
from ...models.filesystem import RangeInFile
from ...models.filesystem_edit import AddDirectory, AddFile
from ..observation import Observation
from ..core import History, Step, StepParams, Policy
from .main import EditCodeStep, RunCodeStep, OpenFileStep
import os
        
class CreatePipelineStep(Step):
    
    api_description: str # "I want to load data from the weatherapi.com API"

    async def run(self, params: StepParams):
        
        await params.run_step(RunCodeStep("python3 -m venv env"))
        await params.run_step(RunCodeStep("source env/bin/activate"))
        await params.run_step(RunCodeStep("pip install dlt"))
        await params.run_step(RunCodeStep("dlt init weather duckdb"))
        await params.run_step(RunCodeStep("pip install -r requirements"))
        await params.run_step(OpenFileStep("weather.py"))

        prompt = '''
        @dlt.resource(write_disposition="append")
        def new_resource(api_secret_key=dlt.secrets.value):
            headers = _create_auth_headers(api_secret_key)

            # make an api call here
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            yield response.json()

        Please edit the function above to call the API described by this:

        "{self.api_description}"
        '''
        resource_function = params.llm.complete(prompt)
        await params.run_step(EditCodeStep(resource_function, RangeInFile(Range(18, 32), "weather.py")))

        await params.run_step(OpenFileStep("./dlt/secrets.toml"))

        return "Please add the API key to `.dlt/secrets.toml` and then press Continue"


class TestPipelineStep(Step):

    async def run(self, params: StepParams):
        await params.run_step(RunCodeStep("python3 weather.py")) # validate that it is 200
        await params.run_step(EditCodeStep("", RangeInFile(Range(44, 44), "weather.py"))) # remove exit()
        await params.run_step(RunCodeStep("python3 weather.py")) # validate that dlt outputted success
        await params.apply_filesystem_edit(AddFile(filepath="query.py", content=""))
        await params.run_step(OpenFileStep("query.py"))
        
        prompt = "Please reply with only Python code that queries the `weather.duckdb` DuckDB instance and use that information to print out the `schema_name.table_name`s to sdout."
        tables_query = '''
        import duckdb

        # Connect to the DuckDB instance
        con = duckdb.connect('weather.duckdb')

        # Query the schema_name.table_name
        result = con.execute("SELECT table_schema || '.' || table_name FROM information_schema.tables WHERE table_schema NOT IN ('information_schema', 'pg_catalog')").fetchall()

        # Print the schema_name.table_name(s) to stdout
        for r in result:
            print(r[0])
        ''' # replace with actual call to LLM that uses database name from previous step
        await params.run_step(EditCodeStep(tables_query, RangeInFile(Range(0, 0), "query.py")))
        await params.run_step(RunCodeStep("python3 query.py"))

        table_name = "weather_data.weather_resource" # should be pulled out output of previous query
        prompt = f"Please reply with only Python code that queries the `weather.duckdb` DuckDB instance for all rows in {table_name} table"
        select_query = f'''
        import duckdb

        # connect to DuckDB instance
        conn = duckdb.connect(database="weather.duckdb")

        # get table names
        rows = conn.execute("SELECT * FROM {table_name};").fetchall()

        # print table names
        for row in rows:
            print(row)
        ''' # replace with actual call to LLM that uses the table names from the previous query
        eof = 100 # how can you define an append???
        beyond = 200 # surely not this
        await params.run_step(EditCodeStep(tables_query, RangeInFile(Range(eof, beyond), "query.py")))
        await params.run_step(RunCodeStep("python3 query.py"))
        return None

class CreatePipelinePolicy(Policy):

    _current_state: str = "init"

    def next(self, history: History=History.from_empty()) -> "Step":
        if self._current_state == "init":
            self._current_state = "create"
            return "What API do I want to load data from?"
        elif self._current_state == "create":
            self._current_state = "test"
            return CreatePipelineStep()
        elif self._current_state == "test":
            self._current_state = "done"
            return TestPipelineStep()
        else:
            return None
    