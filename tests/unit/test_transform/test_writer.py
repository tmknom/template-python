from pathlib import Path

from example.transform.types import DstText
from example.transform.writer import TextWriter
from tests.unit.fake import InMemoryFsWriter


class TestTextWriter:
    """TextWriterクラスのテスト"""

    def test_write_正常系_テキストとパスをパススルーで書き込むこと(self):
        # Arrange
        text = DstText("line1\nline2\nline3")
        path = Path("output/result.txt")
        fs_writer = InMemoryFsWriter()
        writer = TextWriter(fs_writer)

        # Act
        writer.write(text, path)

        # Assert
        assert fs_writer.text == str(text)
        assert fs_writer.file_path == path
