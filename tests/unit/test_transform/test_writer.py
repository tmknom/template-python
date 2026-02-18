from pathlib import Path

from example.foundation.fs import TextFileSystemWriter
from example.transform.writer import TextWriter


class TestTextWriter:
    """TextWriterクラスのテスト"""

    def test_write_正常系_テキストをパススルーで書き込み(self, tmp_path: Path):
        # Arrange
        test_text = "line1\nline2\nline3"
        output_file = tmp_path / "output.txt"

        fs_writer = TextFileSystemWriter()
        writer = TextWriter(fs_writer)

        # Act
        writer.write(test_text, output_file)

        # Assert
        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert content == test_text

    def test_write_正常系_空のテキストを書き込み(self, tmp_path: Path):
        # Arrange
        test_text = ""
        output_file = tmp_path / "empty.txt"

        fs_writer = TextFileSystemWriter()
        writer = TextWriter(fs_writer)

        # Act
        writer.write(test_text, output_file)

        # Assert
        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert content == ""

    def test_write_正常系_日本語テキストを書き込み(self, tmp_path: Path):
        # Arrange
        test_text = "これはテストです\n日本語の行です"
        output_file = tmp_path / "japanese.txt"

        fs_writer = TextFileSystemWriter()
        writer = TextWriter(fs_writer)

        # Act
        writer.write(test_text, output_file)

        # Assert
        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert content == test_text
