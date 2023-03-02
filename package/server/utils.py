from pydantic import BaseModel

class CompletionResponse(BaseModel):
    completion: str