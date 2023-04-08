# Additional Concepts

These are other programming-related concepts central to Continue.

## Position

A line and column number, representing a position in a text file.

## Range

A start and end `Position`

## Filepath

An absolute filepath string and an identifier to the filesystem resource.

## RangeInFile

A `Range` and a `Filepath`.

## FileEdit

A `RangeInFile` and a replacement string. This lets us represent

- Replacements
- Insertions (if the range has same start/end)
- Deletions (if replacement is empty)

## Traceback

A language-agnostic representation of a traceback. Consists of a message string, error type, and a list of `TracebackFrame`s

## TracebackFrame

A `Filepath`, `line number, optional string representing the code at that line, and optional function name.
