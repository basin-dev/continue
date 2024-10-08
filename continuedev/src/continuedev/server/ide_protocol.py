from typing import Any, List
from abc import ABC, abstractmethod

from ..models.main import Traceback
from ..models.filesystem_edit import FileEdit, FileSystemEdit, EditDiff
from ..models.filesystem import RangeInFile


class AbstractIdeProtocolServer(ABC):
    @abstractmethod
    async def handle_json(self, data: Any):
        """Handle a json message"""

    @abstractmethod
    def showSuggestion():
        """Show a suggestion to the user"""

    @abstractmethod
    async def getWorkspaceDirectory(self):
        """Get the workspace directory"""

    @abstractmethod
    async def setFileOpen(self, filepath: str, open: bool = True):
        """Set whether a file is open"""

    @abstractmethod
    async def openNotebook(self):
        """Open a notebook"""

    @abstractmethod
    async def showSuggestionsAndWait(self, suggestions: List[FileEdit]) -> bool:
        """Show suggestions to the user and wait for a response"""

    @abstractmethod
    def onAcceptRejectSuggestion(self, suggestionId: str, accepted: bool):
        """Called when the user accepts or rejects a suggestion"""

    @abstractmethod
    def onTraceback(self, traceback: Traceback):
        """Called when a traceback is received"""

    @abstractmethod
    def onFileSystemUpdate(self, update: FileSystemEdit):
        """Called when a file system update is received"""

    @abstractmethod
    def onCloseNotebook(self, session_id: str):
        """Called when a notebook is closed"""

    @abstractmethod
    def onOpenNotebookRequest(self):
        """Called when a notebook is requested to be opened"""

    @abstractmethod
    async def getOpenFiles(self) -> List[str]:
        """Get a list of open files"""

    @abstractmethod
    async def getHighlightedCode(self) -> List[RangeInFile]:
        """Get a list of highlighted code"""

    @abstractmethod
    async def readFile(self, filepath: str) -> str:
        """Read a file"""

    @abstractmethod
    async def readRangeInFile(self, range_in_file: RangeInFile) -> str:
        """Read a range in a file"""

    @abstractmethod
    async def editFile(self, edit: FileEdit):
        """Edit a file"""

    @abstractmethod
    async def applyFileSystemEdit(self, edit: FileSystemEdit) -> EditDiff:
        """Apply a file edit"""

    @abstractmethod
    async def saveFile(self, filepath: str):
        """Save a file"""
