from typing import List
from ...models.filesystem import FileEdit

# Utilities to convert FileEditWithFullContents to FileDiff,
# and to merge multiple FileDiffs into one compressed FileDiff.
def merge_file_edit(previous: List[FileEdit], new: FileEdit) -> List[FileEdit]:
    # Not necessary for compression purposes necessarily. Mostly just so you can explain it easier.
    pass
