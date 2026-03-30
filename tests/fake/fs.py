from pathlib import Path


class InMemoryFsReader:
    """TextFileSystemReaderProtocol の InMemory 実装"""

    def __init__(self, contents: dict[str, str]) -> None:
        self._contents = contents

    def read(self, file_path: Path) -> str:
        return self._contents[str(file_path)]


class InMemoryFsWriter:
    """TextFileSystemWriterProtocol の InMemory 実装"""

    def __init__(self) -> None:
        self._written: dict[str, str] = {}

    def write(self, text: str, file_path: Path) -> None:
        self._written[str(file_path)] = text

    @property
    def written(self) -> dict[str, str]:
        return dict(self._written)
