from pathlib import Path

from example.transform.reader import TextReader
from example.transform.types import SrcText
from tests.fake.fs import InMemoryFsReader


class TestTextReader:
    """TextReaderクラスのテスト"""

    def test_read_正常系_指定パスのコンテンツを返すこと(self):
        # Arrange
        path = Path("some/file.txt")
        fs_reader = InMemoryFsReader(contents={"some/file.txt": "test text"})
        reader = TextReader(fs_reader)

        # Act
        result = reader.read(path)

        # Assert
        assert result == SrcText("test text")
