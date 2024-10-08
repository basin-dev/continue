# This is a separate server from server/main.py
import asyncio
import os
from typing import Any, Dict, List, Type, TypeVar, Union
import uuid
from fastapi import WebSocket, Body, APIRouter
from uvicorn.main import Server

from ..libs.util.queue import AsyncSubscriptionQueue
from ..models.filesystem import FileSystem, RangeInFile, EditDiff, RealFileSystem
from ..models.main import Traceback
from ..models.filesystem_edit import AddDirectory, AddFile, DeleteDirectory, DeleteFile, FileSystemEdit, FileEdit, FileEditWithFullContents, RenameDirectory, RenameFile, SequentialFileSystemEdit
from pydantic import BaseModel
from .notebook import SessionManager, session_manager
from .ide_protocol import AbstractIdeProtocolServer


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


class FileEditsUpdate(BaseModel):
    messageType: str = "fileEdits"
    fileEdits: List[FileEditWithFullContents]


class OpenFilesResponse(BaseModel):
    messageType: str = "openFiles"
    openFiles: List[str]


class HighlightedCodeResponse(BaseModel):
    messageType: str = "highlightedCode"
    highlightedCode: List[RangeInFile]


class ShowSuggestionRequest(BaseModel):
    messageType: str = "showSuggestion"
    suggestion: FileEdit


class ShowSuggestionResponse(BaseModel):
    messageType: str = "showSuggestion"
    suggestion: FileEdit
    accepted: bool


class ReadFileResponse(BaseModel):
    messageType: str = "readFile"
    contents: str


class EditFileResponse(BaseModel):
    messageType: str = "editFile"
    fileEdit: FileEditWithFullContents


class WorkspaceDirectoryResponse(BaseModel):
    messageType: str = "workspaceDirectory"
    workspaceDirectory: str


T = TypeVar("T", bound=BaseModel)


class IdeProtocolServer(AbstractIdeProtocolServer):
    websocket: WebSocket
    session_manager: SessionManager
    sub_queue: AsyncSubscriptionQueue = AsyncSubscriptionQueue()

    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager

    async def _send_json(self, data: Any):
        await self.websocket.send_json(data)

    async def _receive_json(self, message_type: str) -> Any:
        return await self.sub_queue.get(message_type)

    async def _send_and_receive_json(self, data: Any, resp_model: Type[T], message_type: str) -> T:
        await self._send_json(data)
        resp = await self._receive_json(message_type)
        return resp_model.parse_obj(resp)

    async def handle_json(self, data: Any):
        t = data["messageType"]
        if t == "openNotebook":
            await self.openNotebook()
        elif t == "setFileOpen":
            await self.setFileOpen(data["filepath"], data["open"])
        elif t == "fileEdits":
            fileEdits = list(
                map(lambda d: FileEditWithFullContents.parse_obj(d), data["fileEdits"]))
            self.onFileEdits(fileEdits)
        elif t in ["highlightedCode", "openFiles", "readFile", "editFile", "workspaceDirectory"]:
            self.sub_queue.post(t, data)
        else:
            raise ValueError("Unknown message type", t)

    # ------------------------------- #
    # Request actions in IDE, doesn't matter which Session
    def showSuggestion():
        pass

    async def setFileOpen(self, filepath: str, open: bool = True):
        # Agent needs access to this.
        await self.websocket.send_json({
            "messageType": "setFileOpen",
            "filepath": filepath,
            "open": open
        })

    async def openNotebook(self):
        session_id = self.session_manager.new_session(self)
        await self._send_json({
            "messageType": "openNotebook",
            "sessionId": session_id
        })

    async def showSuggestionsAndWait(self, suggestions: List[FileEdit]) -> bool:
        ids = [str(uuid.uuid4()) for _ in suggestions]
        for i in range(len(suggestions)):
            self._send_json({
                "messageType": "showSuggestion",
                "suggestion": suggestions[i],
                "suggestionId": ids[i]
            })
        responses = await asyncio.gather(*[
            self._receive_json(ShowSuggestionResponse)
            for i in range(len(suggestions))
        ])  # WORKING ON THIS FLOW HERE. Fine now to just await for response, instead of doing something fancy with a "waiting" state on the agent.
        # Just need connect the suggestionId to the IDE (and the notebook)
        return any([r.accepted for r in responses])

    # ------------------------------- #
    # Here needs to pass message onto the Agent OR Agent just subscribes.
    # This is where you might have triggers: plugins can subscribe to certian events
    # like file changes, tracebacks, etc...

    def onAcceptRejectSuggestion(self, suggestionId: str, accepted: bool):
        pass

    def onTraceback(self, traceback: Traceback):
        # Same as below, maybe not every agent?
        for _, session in self.session_manager.sessions.items():
            session.agent.handle_traceback(traceback)

    def onFileSystemUpdate(self, update: FileSystemEdit):
        # Access to Agent (so SessionManager)
        pass

    def onCloseNotebook(self, session_id: str):
        # Accesss to SessionManager
        pass

    def onOpenNotebookRequest(self):
        pass

    def onFileEdits(self, edits: List[FileEditWithFullContents]):
        # Send the file edits to ALL agents.
        # Maybe not ideal behavior
        for _, session in self.session_manager.sessions.items():
            session.agent.handle_manual_edits(edits)

    # Request information. Session doesn't matter.
    async def getOpenFiles(self) -> List[str]:
        resp = await self._send_and_receive_json({
            "messageType": "openFiles"
        }, OpenFilesResponse, "openFiles")
        return resp.openFiles

    async def getWorkspaceDirectory(self) -> str:
        resp = await self._send_and_receive_json({
            "messageType": "workspaceDirectory"
        }, WorkspaceDirectoryResponse, "workspaceDirectory")
        return resp.workspaceDirectory

    async def getHighlightedCode(self) -> List[RangeInFile]:
        resp = await self._send_and_receive_json({
            "messageType": "highlightedCode"
        }, HighlightedCodeResponse, "highlightedCode")
        return resp.highlightedCode

    async def readFile(self, filepath: str) -> str:
        """Read a file"""
        resp = await self._send_and_receive_json({
            "messageType": "readFile",
            "filepath": filepath
        }, ReadFileResponse, "readFile")
        return resp.contents

    async def saveFile(self, filepath: str):
        """Save a file"""
        await self._send_json({
            "messageType": "saveFile",
            "filepath": filepath
        })

    async def readRangeInFile(self, range_in_file: RangeInFile) -> str:
        """Read a range in a file"""
        full_contents = await self.readFile(range_in_file.filepath)
        return FileSystem.read_range_in_str(full_contents, range_in_file.range)

    async def editFile(self, edit: FileEdit) -> FileEditWithFullContents:
        """Edit a file"""
        resp = await self._send_and_receive_json({
            "messageType": "editFile",
            "edit": edit.dict()
        }, EditFileResponse, "editFile")
        return resp.fileEdit

    async def applyFileSystemEdit(self, edit: FileSystemEdit) -> EditDiff:
        """Apply a file edit"""
        backward = None
        fs = RealFileSystem()
        if isinstance(edit, FileEdit):
            file_edit = await self.editFile(edit)
            _, diff = FileSystem.apply_edit_to_str(
                file_edit.fileContents, file_edit.fileEdit)
            backward = diff.backward
        elif isinstance(edit, AddFile):
            fs.write(edit.filepath, edit.content)
            backward = DeleteFile(filepath=edit.filepath)
        elif isinstance(edit, DeleteFile):
            contents = await self.readFile(edit.filepath)
            backward = AddFile(filepath=edit.filepath, content=contents)
            fs.delete_file(edit.filepath)
        elif isinstance(edit, RenameFile):
            fs.rename_file(edit.filepath, edit.new_filepath)
            backward = RenameFile(filepath=edit.new_filepath,
                                  new_filepath=edit.filepath)
        elif isinstance(edit, AddDirectory):
            fs.add_directory(edit.path)
            backward = DeleteDirectory(path=edit.path)
        elif isinstance(edit, DeleteDirectory):
            # This isn't atomic!
            backward_edits = []
            for root, dirs, files in os.walk(edit.path, topdown=False):
                for f in files:
                    path = os.path.join(root, f)
                    edit_diff = await self.applyFileSystemEdit(DeleteFile(filepath=path))
                    backward_edits.append(edit_diff)
                for d in dirs:
                    path = os.path.join(root, d)
                    edit_diff = await self.applyFileSystemEdit(DeleteDirectory(path=path))
                    backward_edits.append(edit_diff)

            edit_diff = await self.applyFileSystemEdit(DeleteDirectory(path=edit.path))
            backward_edits.append(edit_diff)
            backward_edits.reverse()
            backward = SequentialFileSystemEdit(edits=backward_edits)
        elif isinstance(edit, RenameDirectory):
            fs.rename_directory(edit.path, edit.new_path)
            backward = RenameDirectory(path=edit.new_path, new_path=edit.path)
        elif isinstance(edit, FileSystemEdit):
            diffs = []
            for edit in edit.next_edit():
                edit_diff = await self.applyFileSystemEdit(edit)
                diffs.append(edit_diff)
            backward = EditDiff.from_sequence(diffs=diffs).backward
        else:
            raise TypeError("Unknown FileSystemEdit type: " + str(type(edit)))

        return EditDiff(
            forward=edit,
            backward=backward
        )


ideProtocolServer = IdeProtocolServer(session_manager)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Accepted websocket connection from, ", websocket.client)
    await websocket.send_json({"messageType": "connected"})
    ideProtocolServer.websocket = websocket
    while True:
        data = await websocket.receive_json()
        await ideProtocolServer.handle_json(data)

    await websocket.close()
