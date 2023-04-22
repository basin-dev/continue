
import duckdb

# connect to DuckDB instance
conn = duckdb.connect(database="weather.duckdb")

# get table names
rows = conn.execute("SELECT * FROM weather_api.weather_api_resource;").fetchall()

# print table names
for row in rows:
    print(row)
        