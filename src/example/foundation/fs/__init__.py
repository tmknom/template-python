"""Fsパッケージの公開API

Docs:
    - docs/specs/foundation/fs/requirements.md
    - docs/specs/foundation/fs/design.md
"""

from example.foundation.fs.text import TextFileSystemReader, TextFileSystemWriter

__all__ = [
    "TextFileSystemReader",
    "TextFileSystemWriter",
]
