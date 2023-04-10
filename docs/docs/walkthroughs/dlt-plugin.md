# `dlt` Plugin

```python

from plugins import step
from ....libs.steps import StepParams
from ??? import ModelNamePipelineStep

class SetupGPT4Step(Step):

    @step.hookimpl
    def run(params: StepParams) -> Observation:
        params.runner.run(SetSystemMessageStep(...))
        params.runner.run(SetDynamicContextWindowStep(...))
        params.runner.run(SetDynamicMaxResponseLengthStep(...))

```

```python

from plugins import step
from ....libs.steps import StepParams
from ??? import ModelNamePipelineStep

class AskAPIStep(Step):

    @step.hookimpl
    def run(params: StepParams) -> Observation:
        # should pause and wait until user provides an answer
        return "What API do I want to load data from? The destination of the dlt pipeline will be DuckDB"

```

```python

from plugins import step
from ....libs.steps import StepParams
from ??? import ModelNamePipelineStep

class InitPipelineStep(Step):

    @step.hookimpl
    def run(params: StepParams) -> Observation:
        requested_api = # how can I pass in the API name in from the user?
        source_name = params.runner.run(NamePipelineStep(requested_api))
        params.runner.run(CLICommand('dlt init {source_name} duckdb')
        params.runner.run(GPT4Step('...') # but I want to append it to the what API to use?
        
```


```python

from plugins import step
from ....libs.steps import StepParams
from ??? import CLICommand

class AddAPIKeyStep(Step):

    @step.hookimpl
    def run(params: StepParams) -> Observation:
        # should pause until user takes manual action to add API key to the secrets.toml file
        return "Please add the API key to the `secrets.toml` file. I will continue working on the pipeline once it is there"

```

```python

from plugins import step
from ....libs.steps import StepParams
from ??? import CLICommand

class CheckAPIReturnsStep(Step):

    @step.hookimpl
    def run(params: StepParams) -> Observation:
        # runs once there is an api key in `secrets.toml`
        output = params.runner.run(CLICommand('python3 {source_name}.py')
        params.runner.run(CheckAPISuccessStep(output))

```

```python

class createPipelinePolicy(Policy):

    def __init__(self, base_policy: Policy):
        SequentialPolicyWithValidators([SetUpGPT4Step(), SelectAPIStep(), InitPipelineStep(), AddAPIKeyStep(), CheckAPIReturnsStep(), CheckLoadWorksStep(), RefinementStep()], validators=[PythonTracebackValidator()]

```

# Old

`dlt` agent

Policy
- `CreatePipelinePolicy`

dlt_policy = )

Steps
- "Runs code + if error: fix and run again in loop" action
- "Passes natural language instructions to OpenAI model" action (for open-ended refinements)
- "Accepts `dlt` commands and runs them" action
- "If `init` command: kickoff create a pipeline steps" action
- then "What API should I use?" action
- then "Waiting for you to add your API key" action
- then "API success? if so: remove exit()" action
- then "success to DuckDB" action

1. User enters: `dlt init weather duckdb` into the notebook-like GUI

2. `dlt` autopilot triggers `createPipelinePolicy` to assist the user in building their `dlt` pipeline

3. The autopilot uses the `gpt-4` model if possible; otherwise, it falls backs to `gpt-3.5-turbo`. In either case, it uses the following system message:
```
[System]

You are an AI assitant working collaboratively with a user to create a data load tool (dlt) pipeline.

If you don't have enough information, you can request more from the user.

Otherwise:
- Follow the user's requirements carefully and to the letter.
- First think step-by-step--describe your plan for what you want to build in pseudocode, written in great detail.
- Then output the code in a single block.
```

4. The `createPipelinePolicy` takes the action to initialize a pipeline with the `dlt init weather duckdb` command

5. The `createPipelinePolicy` takes the action to send this message via `user` to the OpenAI model:

I got started by running the command `dlt init weather duckdb` in the shell.

This created the following directory structure:
├── .dlt
│   ├── .pipelines
│   ├── config.toml
│   └── secrets.toml
├── weather
│   └── __pycache__
│   └── __init__.py
├── .gitignore
├── weather_pipeline.py
└── requirements.txt

The `weather_pipeline.py` looks like this to begin:
```python
import dlt
import requests


@dlt.source
def weather_source(api_secret_key=dlt.secrets.value):
    return weather_resource(api_secret_key)


def _create_auth_headers(api_secret_key):
    """Constructs Bearer type authorization header which is the most common authorization method"""
    headers = {
        "Authorization": f"Bearer {api_secret_key}"
    }
    return headers


@dlt.resource(write_disposition="append")
def weather_resource(api_secret_key=dlt.secrets.value):
    headers = _create_auth_headers(api_secret_key)

    # check if authentication headers look fine
    print(headers)

    # make an api call here
    # response = requests.get(url, headers=headers, params=params)
    # response.raise_for_status()
    # yield response.json()

    # test data for loading validation, delete it once you yield actual data
    test_data = [{'id': 0}, {'id': 1}]
    yield test_data


if __name__=='__main__':
    # configure the pipeline with your destination details
    pipeline = dlt.pipeline(pipeline_name='weather', destination='duckdb', dataset_name='weather_data')

    # print credentials by running the resource
    data = list(weather_resource())

    # print the data yielded from resource
    print(data)
    exit()

    # run the pipeline with your parameters
    load_info = pipeline.run(weather_source())

    # pretty print the information on data that was loaded
    print(load_info)
```

6. Wait and ask what API to use?

7. The OpenAI API responds to the action with the following:

Sure, I can help you with that. Here's my plan:

1. Define a function to extract data from the weather API using the `requests` module.
2. Update the `weather_resource()` function to use the new function to extract data from the weather API.
3. Add a `transform()` function to the pipeline to process the data before loading it into the destination.
4. Update the `pipeline` object to include the new `transform()` function.

Here's the code:

```python
import dlt
import requests


def extract_weather_data(api_secret_key):
    """Extracts weather data from the API"""
    url = "https://api.weatherapi.com/v1/current.json"
    params = {
        "q": "London",
    }
    headers = {
        "Authorization": f"Bearer {api_secret_key}"
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


@dlt.source
def weather_source(api_secret_key=dlt.secrets.value):
    return weather_resource(api_secret_key)


@dlt.resource(write_disposition="append")
def weather_resource(api_secret_key=dlt.secrets.value):
    data = extract_weather_data(api_secret_key)
    return data

if __name__=='__main__':
    # configure the pipeline with your destination details
    pipeline = dlt.pipeline(pipeline_name='weather', destination='duckdb', dataset_name='weather_data')

    # print credentials by running the resource
    data = list(weather_resource())

    # print the data yielded from resource
    print(data)
    exit()

    # run the pipeline with your parameters
    load_info = pipeline.run(weather_source())

    # pretty print the information on data that was loaded
    print(load_info)
```

7. The `createPipelinePolicy` updates `weather_pipeline.py` with the code from above

8. The `createPipelinePolicy` then prompts the user: "Please add your API key to `.dlt/secrets.toml`" and then press continue

9. User adds their API key to `.dlt/secrets.toml` and presses continue

10. The `createPipelinePolicy` runs the code and sees that `print(data)` prints out what is expected

11. The `createPipelinePolicy` removes the `exit()` from the code

12. The `createPipelinePolicy` runs the code again it loads to the DuckDB instance

13. Maybe policy also print out DuckDB tables, writes a SQL query based on the table, and sees if it works?

14. Then, leaves it open ended for the user to describe how they want to evolve this further (add pagination, more API endpoints, refactor for performance, change to incremental loading, add docstrings, get more parameters from API, add code to transform data before loading it into dlt, etc.)

Other thoughts
- In between any of these steps, it should run to see if there are errors and then fix automatically (but what about API rate limits???)
- In between any of these steps, it should be possible to go on tangents to refine code with natural language instructions
- There probably needs to be a `refinePipelinePolicy`, `prepForProdPipelinePolicy`, etc.
- How are policies selected? Now we are getting into the problem of dialogue management
- How to let foundation model decide when it has more to do?
- See this for how I did this was OpenAI Playground chat mode interface: https://github.com/basin-dev/model-coding-ux-experiments/tree/main/making-a-dlt-pipeline
