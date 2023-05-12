# Step

A step is

## Step methods

### `run` (required)

the code that should run when executed by the policy

### `description` (optional)

the definition of what the step does in natural language

### `reverse` (optional)

the code that should run when the step is reversed

### `modify` (optional)

the code that should run when the step is rerun with feedback

## Steps

### Core

#### RunCommandStep

#### EditCodeStep

### Community

#### CreateTableStep

Create a table in TypeORM

**Q: how can we allow folks to add configurability to their steps (e.g. path where to store generated tests)?**

#### MigrationStep

Create and run an alembic migration

##### Parameters

- `edited_file`: 

#### WritePytestsStep

Write unit tests for this file.

##### Parameters

- for_filepath (required): the path of the file that unit tests should be created for