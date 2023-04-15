# This is a separate server from server/main.py
from typing import Any, List, Type, TypeVar, Union
from fastapi import WebSocket, Body, APIRouter
from uvicorn.main import Server
from ..models.filesystem import RangeInFile
from ..models.main import Traceback
from ..models.filesystem_edit import FileSystemEdit, FileEdit
from pydantic import BaseModel
from .notebook import SessionManager, session_manager
from ..libs.core import Agent
from ..libs.llm.openai import OpenAI
from ..libs.policy import DemoPolicy
import os
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")


def create_demo_agent(ide: "IdeProtocolServer") -> Agent:
    cmd = "python3 /Users/natesesti/Desktop/continue/extension/examples/python/main.py"
    return Agent(llm=OpenAI(api_key=openai_api_key),
                 policy=DemoPolicy(cmd=cmd), ide=ide)


router = APIRouter(prefix="/ide", tags=["ide"])


# Graceful shutdown by closing websockets
original_handler = Server.handle_exit


class AppStatus:
    should_exit = False

    @staticmethod
    def handle_exit(*args, **kwargs):
        AppStatus.should_exit = True
        print("Shutting down")
        original_handler(*args, **kwargs)


Server.handle_exit = AppStatus.handle_exit

# TYPES #


class OpenFilesResponse(BaseModel):
    messageType: str = "openFiles"
    openFiles: List[str]


class HighlightedCodeResponse(BaseModel):
    messageType: str = "highlightedCode"
    highlightedCode: List[RangeInFile]


class ShowSuggestionRequest(BaseModel):
    messageType: str = "showSuggestion"
    suggestion: FileEdit


T = TypeVar("T", bound=BaseModel)


class IdeProtocolServer:
    websocket: WebSocket
    session_manager: SessionManager

    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager

    async def _send_json(self, data: Any):
        print("Sending: ", data)
        await self.websocket.send_json(data)

    async def _receive_json(self) -> Any:
        return await self.websocket.receive_json()

    async def _send_and_receive_json(self, data: Any, resp_model: Type[T]) -> T:
        await self._send_json(data)
        resp = await self._receive_json()
        return resp_model.parse_obj(resp)

    async def handle_json(self, data: Any):
        t = data["messageType"]
        if t == "openNotebook":
            await self.openNotebook()
        elif t == "setFileOpen":
            await self.setFileOpen(data["filepath"], data["open"])
        else:
            raise ValueError("Unknown message type", t)

    # ------------------------------- #

    # Request actions in IDE, doesn't matter which Session
    def showSuggestion():
        pass

    async def setFileOpen(self, filepath: str, open: bool):
        # Agent needs access to this.
        await self.websocket._send_json({
            "messageType": "setFileOpen",
            "filePath": filepath,
            "open": open
        })

    async def openNotebook(self):
        agent = create_demo_agent(self)
        session_id = self.session_manager.new_session(agent)
        agent.run_policy()
        await self._send_json({
            "messageType": "openNotebook",
            "sessionId": session_id
        })

    # Here needs to pass message onto the Agent OR Agent just subscribes.
    # This is where you might have triggers: plugins can subscribe to certian events
    # like file changes, tracebacks, etc...

    def onAcceptRejectSuggestion(self, suggestionId: str, accepted: bool):
        pass

    def onTraceback(self, traceback: Traceback):
        pass

    def onFileSystemUpdate(self, update: FileSystemEdit):
        # Access to Agent (so SessionManager)
        pass

    def onCloseNotebook(self, session_id: str):
        # Accesss to SessionManager
        pass

    def onOpenNotebookRequest(self):
        pass

    # Request information. Session doesn't matter.
    async def getOpenFiles(self) -> List[str]:
        resp = await self._send_and_receive_json({
            "messageType": "getOpenFiles"
        }, OpenFilesResponse)
        return resp.openFiles

    async def getHighlightedCode(self) -> List[RangeInFile]:
        resp = await self._send_and_receive_json({
            "messageType": "getHighlightedCode"
        }, HighlightedCodeResponse)
        return resp.highlightedCode


ideProtocolServer = IdeProtocolServer(session_manager)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    ideProtocolServer.websocket = websocket
    await websocket.send_json({"messageType": "connected"})

    while True:
        data = await websocket.receive_json()
        print("Received", data)
        await ideProtocolServer.handle_json(data)

    await websocket.close()
