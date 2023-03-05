from pydantic import BaseModel

class CompletionResponse(BaseModel):
    completion: str

class OptionalCompletionResponse(BaseModel):
    completion: str | None = None