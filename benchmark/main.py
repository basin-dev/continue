from bugswarm.common.rest_api.database_api import DatabaseAPI
bugswarmapi = DatabaseAPI() # (token='AN_OPTIONAL_TOKEN')
api_filter = '{"reproduce_successes":{"$gt":0, "$lt":5}, "lang":"Python"}'
resp = bugswarmapi.filter_artifacts(api_filter)

