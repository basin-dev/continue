# `dlt` Plugin

Demo

0. Nate narrates a video of me creating a dlt pipeline using chatgpt (e.g. "he has done this dozens of times, he knows every step he will need to do, he uses chatgpt to speed himself up, but he still can't type fast enough") and then switches to code for the Continue plugin for creating a dlt pipeline at the end
1. Nate says "Instead of using ChatGPT to create new dlt pipeline, Ty now uses a Continue plug-in he wrote to accelerate the process of creating a dlt pipeline that he plans to share it with the dlt community. Let's see it in action."
2. Nate then switches to Continue and shows how "We can kickoff the plug-in with the `/dlt` command"
3. This causes Continue to ask: "What API do you want to load data from using a dlt pipeline?" It then waits for input from the user.
4. Nate types in something like "I want to load data from a free weather API"
5. The plug-in runs `dlt init weather duckdb`, creating a `weather.py` file
7. It then asks GPT-3.5-turbo to select a weather API, write out a plan for implementing a dlt pipeline, and then it implements the resource function to call the WeatherAPI.com API and get the latest weather for London
8. It follows this by pausing and prompting Nate to add his API key to `.dlt/secrets.toml`
9. Nate manually edits `weather.py`, replacing London with SF, showing this is possible during a plug-in
10. Continue then resumes the plug-in and prompts Nate to add his API key to `.dlt/secrets.toml`
11. Nate then grabs his key from weatherapi.com and pastes it into `.dlt/secrets.toml`, pressing continue to move forward
12. It then runs ``weather.py`, which tries to call the API, and it sees that it returns a 200 response and valid json is printed out (ideally an error occurs in the code it wrote, which is automatically fixed before it works)
13. It then makes an edit to remove the `exit()` from the main file
14. It then runs `weather.py`, which this time loads the data into the `weather.duckdb` DuckDB instance
15. It then writes a utility function to SQL query `weather.duckdb` for the tables and schemas
16. It then runs this and prints out the schema
17. It then adds a second utility function to SQL query `weather.duckdb` for some of the data in one of the table using the schema
18. It pauses. Nate realizes that he does not want to load all of the data. Just a subset of it. So he goes to #13 and asks for it to add transform function that leaves out the temp in celsius. Steps 14-17 replay
19. Nate then asks for it to add unit tests for the transform function and the DuckDB utility function. It runs them


```python

from plugins import step
from ....libs.steps import StepParams
from ??? import ModelNamePipelineStep

params.llm

params.run_step(NaturalLanguageUserInputStep(“…question…?”))

class SetupGPT4Step(Step):

    @step.hookimpl
    def run(params: StepParams) -> Observation:
        params.run_step(SetSystemMessageStep(...))
        params.run_step(SetDynamicContextWindowStep(...))
        params.run_step(SetDynamicMaxResponseLengthStep(...))

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
        source_name = params.run_step(NamePipelineStep(requested_api))
        params.run_step(CLICommand('dlt init {source_name} duckdb')
        params.run_step(GPT4Step('...') # but I want to append it to the what API to use?

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
        output = params.run_step(CLICommand('python3 {source_name}.py')
        params.run_step(CheckAPISuccessStep(output))

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

1. User enters: `` into the notebook-like GUI

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
│ ├── .pipelines
│ ├── config.toml
│ └── secrets.toml
├── weather
│ └── **pycache**
│ └── **init**.py
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
