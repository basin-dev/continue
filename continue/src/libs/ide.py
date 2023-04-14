# This is a separate server from server/main.py
from typing import Any, List, Type, TypeVar, Union
from fastapi import FastAPI, Header, WebSocket, Body
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from ..models.filesystem import RangeInFile
from ..models.main import Traceback
from ..models.filesystem_edit import FileSystemEdit, FileEdit
from pydantic import BaseModel


app = FastAPI()

# Add CORS support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TYPES #


class OpenFilesResponse(BaseModel):
    msg_type: str = "openFiles"
    openFiles: List[str]


class HighlightedCodeResponse(BaseModel):
    msg_type: str = "highlightedCode"
    highlightedCode: List[RangeInFile]


class ShowSuggestionRequest(BaseModel):
    msg_type: str = "showSuggestion"
    suggestion: FileEdit


T = TypeVar("T", bound=BaseModel)


class IdeProtocolServer:
    websocket: WebSocket
    session_manager: "SessionManager"

    def start(self):
        uvicorn.run(app, host="http://localhost:8001", port=8001)

    async def _send_json(self, data: Any):
        await self.websocket.send_json()

    async def _receive_json(self) -> Any:
        return await self.websocket.receive_json()

    async def _send_and_receive_json(self, data: Any, resp_model: Type[T]) -> T:
        await self._send_json(data)
        resp = await self._receive_json()
        return resp_model.parse_obj(resp)

    # ------------------------------- #

    # Request actions in IDE, doesn't matter which Session
    def showSuggestion():
        pass

    async def setFileOpen(self, filepath: str, open: bool):
        # Agent needs access to this.
        await self.websocket._send_json({
            "type": "setFileOpen",
            "filePath": filepath,
            "open": open
        })

    async def openNotebook(self, session_id: str):
        # Where is it decided when a new session should be started?
        # This is what hooks are for??
        pass

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
            "msg_type": "getOpenFiles"
        }, OpenFilesResponse)
        return resp.openFiles

    async def getHighlightedCode(self) -> List[RangeInFile]:
        resp = await self._send_and_receive_json({
            "msg_type": "getHighlightedCode"
        }, HighlightedCodeResponse)
        return resp.highlightedCode


server = IdeProtocolServer()

# And then these methods will just be provided through StepParams??

# This seems highly coupled to SessionManager.
# It also knows a good deal about Agent.
