"""TextFileSystemReaderProtocol の InMemory 実装"""

from pathlib import Path


class InMemoryFsReader:
    """TextFileSystemReaderProtocol の InMemory 実装"""

    def __init__(self, text: str = ""):
        self.text = text
        self.file_path: Path | None = None

    def read(self, file_path: Path) -> str:
        self.file_path = file_path
        return self.text


class InMemoryFsWriter:
    """TextFileSystemWriterProtocol の InMemory 実装"""

    def __init__(self):
        self.text: str | None = None
        self.file_path: Path | None = None

    def write(self, text: str, file_path: Path) -> None:
        self.text = text
        self.file_path = file_path
