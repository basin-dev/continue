from fastapi import FastAPI
from debug import router as debug_router
from ds_gen import router as docstring_router
from test_gen import router as unittest_router

app = FastAPI()
app.include_router(debug_router)
app.include_router(docstring_router)
app.include_router(unittest_router)

@app.get("/test")
def test():
    return "Success"