"""プロトコル定義の公開API（OnionアーキテクチャのPort定義）。

公開APIは `example.protocol` から import すること(`__all__` のみ互換性対象)。
"""

from example.protocol.fs import TextFileSystemReaderProtocol, TextFileSystemWriterProtocol

__all__ = [
    "TextFileSystemReaderProtocol",
    "TextFileSystemWriterProtocol",
]
