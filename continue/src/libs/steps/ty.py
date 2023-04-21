from textwrap import dedent
from typing import Coroutine
from ...models.main import Range
from ...models.filesystem import RangeInFile
from ...models.filesystem_edit import AddDirectory, AddFile
from ..observation import Observation, TextObservation
from ..core import History, Step, StepParams, Policy
from .main import EditCodeStep, RunCommandStep, WaitForUserInputStep, WaitForUserConfirmationStep
from ..llm import LLM
import os


class SetupPipelineStep(Step):
    
    api_description: str # e.g. "I want to load data from the weatherapi.com API"

    async def run(self, params: StepParams):
        
        source_name = 'weather' # TODO: replace with LLM determined name
        filename = f'{source_name}.py'

        # running commands to get started when creating a new dlt pipeline
        await params.run_step(RunCommandStep(cmd=f'python3 -m venv env'))
        await params.run_step(RunCommandStep(cmd=f'source env/bin/activate'))
        await params.run_step(RunCommandStep(cmd=f'pip install dlt'))
        await params.run_step(RunCommandStep(cmd=f'dlt init {source_name} duckdb'))
        await params.run_step(RunCommandStep(cmd=f'pip install -r requirements'))

        # editing the resource function to call the requested API
        await params.ide.setFileOpen(filename, True)
        await params.run_step(EditCodeStep(
            range_in_files=[RangeInFile.from_entire_file(filename)],
            prompt=f'Edit the resource function to call the API described by this: {self.api_description}'
        ))

        # Wait for user to put API key in secrets.toml
        await params.ide.setFileOpen(".dlt/secrets.toml", True)
        return WaitForUserConfirmationStep(prompt=f"Please add the API key to the `secrets.toml` file and then press `Continue`")


class ValidatePipelineStep(Step):

    async def run(self, params: StepParams):
        
        source_name = 'weather' # TODO: replace with LLM determined name
        filename = f'{source_name}.py'

        # test that the API call works
        await params.run_step(RunCommandStep(cmd=f'python3 {filename}'))
        # TODO: validate that the response code is 200 (i.e. successful) else loop

        # remove exit() from the main main function
        await params.ide.setFileOpen(filename, True)
        await params.run_step(EditCodeStep(
            range_in_files=[RangeInFile.from_entire_file(filename)],
            prompt=f'Remove exit() from the main function'
        ))

        # test that dlt loads the data into the DuckDB instance
        await params.run_step(RunCommandStep(cmd=f'python3 {filename}'))
        # TODO: validate that `dlt` outputted success via print(load_info) else loop

        # write Python code in `query.py` that queries the DuckDB instance to validate it worked
        await params.apply_filesystem_edit(AddFile(filepath='query.py', content=""))
        await params.ide.setFileOpen('query.py', True)
        names_query_code = '''
        import duckdb

        # Connect to the DuckDB instance
        con = duckdb.connect('weather.duckdb')

        # Query the schema_name.table_name
        result = con.execute("SELECT table_schema || '.' || table_name FROM information_schema.tables WHERE table_schema NOT IN ('information_schema', 'pg_catalog')").fetchall()

        # Print the schema_name.table_name(s) to stdout
        for r in result:
            print(r[0])
        '''
        params.apply_filesystem_edit(EditFile(names_query_code, RangeInFile.from_entire_file('query.py')) # TODO: fix this
        await params.run_step(RunCommandStep(cmd=f'python3 query.py'))
        table_name = "weather_data.weather_resource" # TODO: replace with code that grabs all non-dlt `schema_name.table_name`s outputted by previous query
        tables_query_code = f'''
        import duckdb

        # connect to DuckDB instance
        conn = duckdb.connect(database="weather.duckdb")

        # get table names
        rows = conn.execute("SELECT * FROM {table_name};").fetchall()

        # print table names
        for row in rows:
            print(row)
        '''
        params.apply_filesystem_edit(EditFile(tables_query_code, RangeInFile.from_entire_file('query.py')) # TODO: fix this
        await params.run_step(RunCommandStep(cmd=f'python3 query.py'))

        return None

class CreatePipelinePolicy(Policy):

    _current_state: str = "init"

    def next(self, history: History=History.from_empty()) -> "Step":
        if self._current_state == "init":
            self._current_state = "setup"
            return WaitForUserInputStep(prompt="What API do you want to load data from?")
        elif self._current_state == "setup":
            self._current_state = "validate"
            return SetupPipelineStep()
        elif self._current_state == "validate":
            self._current_state = "done"
            return ValidatePipelineStep()
        else:
            return None