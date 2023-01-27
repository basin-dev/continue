from fastapi import FastAPI
from debug import router as debug_router
from ds_gen import router as docstring_router

app = FastAPI()
app.include_router(debug_router)
app.include_router(docstring_router)