import asyncio
from textwrap import dedent
from typing import Coroutine

from ...models.main import Range
from ...models.filesystem import RangeInFile
from ...models.filesystem_edit import AddDirectory, AddFile
from ..observation import Observation, TextObservation
from ..core import Step, ContinueSDK
from .main import EditCodeStep, EditFileStep, RunCommandStep, ShellCommandsStep, WaitForUserConfirmationStep
import os


class WritePytestsStep(Step):
    for_filepath: str | None = None
    instructions: str = "Write unit tests for this file."

    async def run(self, sdk: ContinueSDK) -> Coroutine[Observation, None, None]:
        if self.for_filepath is None:
            self.for_filepath = (await sdk.ide.getOpenFiles())[0]

        filename = os.path.basename(self.for_filepath)
        dirname = os.path.dirname(self.for_filepath)

        path_dir = os.path.join(dirname, "tests")
        if not os.path.exists(path_dir):
            await sdk.apply_filesystem_edit(AddDirectory(path=path_dir))

        path = os.path.join(path_dir, f"test_{filename}")
        if os.path.exists(path):
            return None

        for_file_contents = await sdk.ide.readFile(self.for_filepath)

        prompt = dedent(f"""This is the file you will write unit tests for:

```python
{for_file_contents}
```

Here are additional instructions:

"{self.instructions}"

Here is a complete set of pytest unit tests:

        """)
        tests = sdk.llm.complete(prompt)
        await sdk.apply_filesystem_edit(AddFile(filepath=path, content=tests))

        return None


class CreatePyplot(Step):
    # Wish there was a way to add import, specify dependency
    name: str = "Create a pyplot"

    async def run(self, sdk: ContinueSDK) -> Coroutine[Observation, None, None]:
        code = dedent("""import matplotlib.pyplot as plt
import numpy as np

{instructions}

plt.xlabel("{x_label}")
plt.ylabel("{y_label}")
plt.title("{title}")
plt.show()
        """)


class ImplementAbstractMethodStep(Step):
    name: str = "Implement abstract method for all subclasses"
    method_name: str = "def walk(self, path: str) -> List[str]"
    class_name: str = "FileSystem"

    async def run(self, sdk: ContinueSDK):
        await sdk.run_step(WaitForUserConfirmationStep(prompt="Detected new abstract method. Implement in all subclasses?"))
        implementations = []
        for filepath in ["/Users/natesesti/Desktop/continue/extension/examples/python/filesystem/real.py", "/Users/natesesti/Desktop/continue/extension/examples/python/filesystem/virtual.py"]:
            contents = await sdk.ide.readFile(filepath)
            implementations.append(
                RangeInFile.from_entire_file(filepath, contents))

        for implementation in implementations:
            await sdk.run_step(EditCodeStep(
                range_in_files=[implementation],
                prompt=f"{{code}}\nRewrite the class, implementing the method `{self.method_name}`.\n",
            ))


class CreateTableStep(Step):
    sql_str: str
    name: str = "Create a table"

    async def run(self, sdk: ContinueSDK) -> Coroutine[Observation, None, None]:
        # Write the TypeORM entity
        entity_name = "Order"
        orm_entity = sdk.llm.complete(
            f"{self.sql_str}\n\nWrite a TypeORM entity called {entity_name} for this table, importing as necessary:")
        # sdk.llm.complete("What is the name of the entity?")
        await sdk.apply_filesystem_edit(AddFile(filepath=f"/Users/natesesti/Desktop/continue/extension/examples/python/MyProject/src/entity/{entity_name}.ts", content=orm_entity))
        await sdk.ide.setFileOpen(f"/Users/natesesti/Desktop/continue/extension/examples/python/MyProject/src/entity/{entity_name}.ts", True)

        # Add entity to data-source.ts
        await sdk.run_step(EditFileStep(
            filepath=f"/Users/natesesti/Desktop/continue/extension/examples/python/MyProject/src/data-source.ts",
            prompt=f"{{code}}\nAdd the {entity_name} entity:\n",
        ))

        # Generate blank migration for the entity
        obs: TextObservation = await sdk.run_step(RunCommandStep(
            cmd=f"npx typeorm migration:create ./src/migration/Create{entity_name}Table"
        ))
        migration_filepath = obs.text.split(" ")[1]

        # Wait for user input
        await sdk.run_step(WaitForUserConfirmationStep(prompt="Fill in the migration?"))

        # Fill in the migration
        await sdk.run_step(EditFileStep(
            filepath=migration_filepath,
            prompt=f"{{code}}\nThis is the table that was created:\n{self.sql_str}\n\nFill in the migration for the table:\n",
        ))

        # Run the migration
        command_step = RunCommandStep(
            cmd=f"""sqlite3 database.sqlite 'CREATE TABLE orders (
  order_id SERIAL PRIMARY KEY,
  customer_id INTEGER,
  order_date DATE,
  order_total NUMERIC,
  shipping_address TEXT,
  billing_address TEXT,
  payment_method TEXT,
  order_status TEXT,
  tracking_number TEXT
);'"""
        )
        command_step._description = "npx typeorm-ts-node-commonjs migration:run -d ./src/data-source.ts"
        await sdk.run_step(command_step)
