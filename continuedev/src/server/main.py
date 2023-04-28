from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .ide import router as ide_router
from .notebook import router as notebook_router

app = FastAPI()

app.include_router(ide_router)
app.include_router(notebook_router)

# Add CORS support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
