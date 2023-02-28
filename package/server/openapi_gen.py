from fastapi.openapi.utils import get_openapi
from .main import app
import json

def get_app_schema(app):
   openapi_schema = get_openapi(
       title="Continue API",
       version="1.0",
       description="Continue API",
       routes=app.routes,
   )
   app.openapi_schema = openapi_schema
   return app.openapi_schema

if __name__ == "__main__":
    with open("schema/openapi.json", "w") as f:
        f.write(json.dumps(get_app_schema(app), indent=2))