"""Protocolパッケージの公開API

Docs:
    - docs/specs/protocol/requirements.md
    - docs/specs/protocol/design.md
"""

from example.protocol.fs import TextFileSystemReaderProtocol, TextFileSystemWriterProtocol

__all__ = [
    "TextFileSystemReaderProtocol",
    "TextFileSystemWriterProtocol",
]
