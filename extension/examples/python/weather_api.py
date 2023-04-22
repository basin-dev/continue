import dlt
from dlt.sources.helpers import requests


@dlt.source
def weather_api_source(api_secret_key=dlt.secrets.value):
    return weather_api_resource(api_secret_key)


def _create_auth_headers(api_secret_key):
    """Constructs Bearer type authorization header which is the most common authorization method"""
    headers = {
        "Authorization": f"Bearer {api_secret_key}"
    }
    return headers


@dlt.resource(write_disposition="append")
def weather_api_resource(api_secret_key=dlt.secrets.value):
    headers = _create_auth_headers(api_secret_key)

    # check if authentication headers look fine

    # make an api call here
    url = 'https://api.weatherapi.com/v1/forecast.json'
    params = {'q': 'London', 'days': '7', 'key': api_secret_key}
    print(headers)
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    yield response.json()


if __name__ == '__main__':
    # configure the pipeline with your destination details
    pipeline = dlt.pipeline(pipeline_name='weather',
                            destination='duckdb', dataset_name='weather_api')

    # print credentials by running the resource
    data = list(weather_api_resource())

    # print the data yielded from resource
    print(data)

    # run the pipeline with your parameters
    load_info = pipeline.run(weather_api_source())

    # pretty print the information on data that was loaded
    print(load_info)
