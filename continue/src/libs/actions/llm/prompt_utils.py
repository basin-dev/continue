from abc import abstractmethod
from typing import Dict, List

from pydantic import BaseModel
from ....models.main import FileEdit, AbstractModel
from ....models.filesystem import FileSystem, RangeInFile

# Even better, you define an encoder/decoder class so people can play around with different ways of doing this. And it can be stateful.

class FileContentsEncoderDecoder(AbstractModel):
    filesystem: FileSystem
    range_in_files: List[RangeInFile]

    def __init__(self, filesystem: FileSystem, range_in_files: List[RangeInFile]):
        self.filesystem = filesystem
        self.range_in_files = range_in_files

    @abstractmethod
    def encode() -> str:
        raise NotImplementedError()
    
    @abstractmethod
    def decode(completion: str) -> List[FileEdit]:
        raise NotImplementedError()
    
    def _suggestions_to_file_edits(self, suggestions: Dict[str, str]) -> List[FileEdit]:
        file_edits: List[FileEdit] = []
        for suggestion_filepath, suggestion in suggestions.items():
            matching_rifs = list(filter(lambda r: r.filepath == suggestion_filepath, self.range_in_files))
            if (len(matching_rifs) > 0):
                range_in_file = matching_rifs[0]
                file_edits.append(FileEdit(
                    range=range_in_file.range,
                    filepath=range_in_file.filepath,
                    replacement=suggestion
                ))

        return file_edits
    
class MarkdownStyleEncoderDecoder(FileContentsEncoderDecoder):
    def encode(self) -> str:
        return "\n\n".join([
            f"File ({rif.filepath})\n```\n{self.filesystem.read_range_in_file(rif)}\n```"
            for rif in self.range_in_files
        ])

    def _decode_to_suggestions(self, completion: str) -> Dict[str, str]:
        # Should do a better job of ensuring the ``` format, but for now the issue is mostly just on single file inputs:
        if len(self.range_in_files) == 0:
            return {}

        if not '```' in completion:
            completion = "```\n" + completion + "\n```"
        if completion.splitlines()[0].strip() == '```':
            first_filepath = self.range_in_files[0].filepath
            completion = f"File ({first_filepath})\n" + completion

        suggestions: Dict[str, str] = {}
        current_file_lines: List[str] = []
        current_filepath: str | None = None
        last_was_file = False
        inside_file = False
        for line in completion.splitlines():
            if line.strip().startswith("File ("):
                last_was_file = True
                current_filepath = line.strip()[6:-1]
            elif last_was_file and line.startswith("```"):
                last_was_file = False
                inside_file = True
            elif inside_file:
                if line.startswith("```"):
                    inside_file = False
                    suggestions[current_filepath] = "\n".join(current_file_lines)
                    current_file_lines = []
                    current_filepath = None
                else:
                    current_file_lines.append(line)

        return suggestions
    
    def decode(self, completion: str) -> List[FileEdit]:
        suggestions = self._decode_to_suggestions(completion)
        file_edits = self._suggestions_to_file_edits(suggestions)
        return file_edits