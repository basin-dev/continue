import subprocess
from textwrap import dedent
from typing import Coroutine
from ...models.main import Position, Range
from ...models.filesystem import RangeInFile
from ...models.filesystem_edit import AddDirectory, AddFile, FileEdit
from ..observation import DictObservation
from ..core import History, Step, ContinueSDK, Policy
from .main import EditCodeStep, RunCommandStep, WaitForUserInputStep, WaitForUserConfirmationStep, ShellCommandsStep
from ..llm import LLM
import os


class SetupPipelineStep(Step):

    api_description: str  # e.g. "I want to load data from the weatherapi.com API"

    async def run(self, sdk: ContinueSDK):
        source_name = sdk.llm.complete(
            f"Write a snake_case name for the data source described by {self.api_description}: ").strip()
        filename = f'{source_name}.py'

        # running commands to get started when creating a new dlt pipeline
        await sdk.run_step(ShellCommandsStep(cmds=[
            'python3 -m venv env',
            'source env/bin/activate',
            'pip install dlt',
            'dlt init {source_name} duckdb',
            'Y',
            'pip install -r requirements.txt'
        ]))

        # editing the resource function to call the requested API
        await sdk.run_step(EditCodeStep(
            filename=filename,
            prompt=f'Edit the resource function to call the API described by this: {self.api_description}'
        ))

        # wait for user to put API key in secrets.toml
        await sdk.ide.setFileOpen(".dlt/secrets.toml")
        await sdk.run_step(WaitForUserConfirmationStep(prompt=f"Please add the API key to the `secrets.toml` file and then press `Continue`"))
        return DictObservation(values={"source_name": source_name})


class ValidatePipelineStep(Step):

    async def run(self, sdk: ContinueSDK):
        source_name = sdk.history.last_observation()["source_name"]
        filename = f'{source_name}.py'

        # test that the API call works
        await sdk.run_step(RunCommandStep(cmd=f'python3 {filename}'))

        # remove exit() from the main main function
        await sdk.run_step(EditCodeStep(
            filename=filename,
            prompt='Remove exit() from the main function'
        ))

        # load the data into the DuckDB instance
        await sdk.run_step(RunCommandStep(cmd=f'python3 {filename}'))

        table_name = f"{source_name}.{source_name}_resource"
        tables_query_code = dedent(f'''
            import duckdb

            # connect to DuckDB instance
            conn = duckdb.connect(database="{source_name}.duckdb")

            # get table names
            rows = conn.execute("SELECT * FROM {table_name};").fetchall()

            # print table names
            for row in rows:
                print(row)
        ''')
        await sdk.apply_filesystem_edit(AddFile(filepath='query.py', content=tables_query_code))
        await sdk.run_step(RunCommandStep(cmd=f'env/bin/python3 query.py'))


class CreatePipelineStep(Step):

    async def run(self, sdk: ContinueSDK):
        await sdk.run_step(
            WaitForUserInputStep(prompt="What API do you want to load data from?") >>
            SetupPipelineStep() >>
            ValidatePipelineStep()
        )
