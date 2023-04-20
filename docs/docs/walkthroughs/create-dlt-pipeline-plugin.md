# `dlt` Plugin

## Using Continue to create a dlt pipeline (without plugin)

1. Run `python3 -m venv env` in the terminal
2. Run `source env/bin/activate` in the terminal
3. Run `pip install dlt` in the terminal
4. Run `dlt init weather duckdb` in the terminal
5. Run `pip install -r requirements` in the terminal
6. Open the `weather.py` file
7. Send Continue "edit the resource function to call the WeatherAPI.com API" (Review step)
8. Copy and paste your API key into `.dlt/secrets.toml`
9. Run `python3 weather.py` in the terminal to see if the API responds with 200 status
10. If so, then manually remove `exit()` from the main function
11. Run `python3 weather.py` in the terminal again
12. Create and open a `query.py` file to make sure expected data is in DuckDB
13. Send Continue "Add Python code to query the weather.duckdb DuckDB instance for its tables" (Review step)
14. Run `python3 query.py` in the terminal and look for the correct {table_name} in the output
15. Send Continue "Add Python code to run a select query on the {table_name} table" (Review step)
16. Run `python3 query.py` in the terminal again and then look if the output is as expected

## Using Continue to create a dlt pipeline (with plugin)

1. Send Continue `/dlt`, and it prompts you for what API to use
2. Send Continue "load data from the WeatherAPI.com API"
3. 1-7 directly above occur, and it prompts you to add your API key to `.dlt/secrets.toml` (Review steps)
4. Copy and paste your API key into `.dlt/secrets.toml` and press Continue button
5. 9-16 above occur and then look if the output is as expected (Review steps)

## Demo Outline

0. Nate narrates a before video of me creating a dlt pipeline using chatgpt (e.g. "he has done this dozens of times, he knows every step he will need to do, he uses chatgpt to speed himself up, but he still can't copy, paste, and type fast enough to keep up with his thoughts") and then switches to code for the Continue plugin for creating a dlt pipeline at the end
1. Nate says "Instead of using ChatGPT to create new dlt pipeline, let's see what it's like to use Continue"
2. Nate switches to Continue and follows steps in `Using Continue to create a dlt pipeline (without plugin)`
3. Nate says "now let's see what's like if to use the Continue plug-in Ty wrote to accelerate the process of creating a dlt pipeline that he plans to share it with the dlt community"
4. Nate then switches to Continue and shows how "We can kickoff the plug-in with the `/dlt` command"
3. This causes Continue to ask: "What API do you want to load data from using a dlt pipeline?" It then waits for input from the user.
4. Nate types in something like "load data from the WeatherAPI.com API"
5. The plug-in runs 1-7 directly below
7. It then asks GPT-3.5-turbo to write out a plan for implementing a dlt pipeline, and then it implements the resource function to call the WeatherAPI.com API
8. It follows this by pausing and prompting Nate to add his API key to `.dlt/secrets.toml`
11. Nate then grabs his key from weatherapi.com and pastes it into `.dlt/secrets.toml`, pressing continue to move forward
12. It then runs `weather.py`, which tries to call the API, and it sees that it returns a 200 response and valid json is printed out (ideally an error occurs in the code it wrote, which is automatically fixed before it works)
13. It then makes an edit to remove the `exit()` from the main file
14. It then runs `weather.py`, which this time loads the data into the `weather.duckdb` DuckDB instance
15. It then creates a `weather.py` file to SQL query `weather.duckdb` for the tables and schemas
16. It then runs this and prints out the schema
17. It then adds code to SQL query `weather.duckdb` for some of the data in the table with the same name as the resource
18. It pauses. With the leftover time, Nate decides he does not want to load all of the data. Just a subset of it. So he goes to #13 and asks for it to add transform function that only loads the most important data points. Steps 14-17 replay
19. Nate then asks for it to add unit tests for the transform function. It runs them and they work