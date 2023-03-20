from typing import Dict, List
from fastapi import APIRouter, Body, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from ..libs.language_models.llm import OpenAI

router = APIRouter(prefix="/chat", tags=["chat"])
llm = OpenAI()

def byte_wrapper(generator):
    for chunk in generator:
        yield bytes(chunk, "utf-8")

@router.get("/test")
async def test(prompt: str) -> StreamingResponse:
    generator = llm.stream_complete(prompt)
    return StreamingResponse(byte_wrapper(generator))


class ChatMessage(BaseModel):
    role: str
    content: str

class ChatHistory(BaseModel):
    messages: List[ChatMessage]

@router.post("/complete")
async def complete(body: ChatHistory) -> StreamingResponse:
    generator = llm.stream_chat(list(map(lambda x: x.dict(), body.messages)))
    return StreamingResponse(byte_wrapper(generator))