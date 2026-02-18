from datetime import datetime
from pathlib import Path

from example.foundation.fs import TextFileSystemReader, TextFileSystemWriter
from example.transform.context import TransformContext
from example.transform.orchestrator import TransformOrchestrator
from example.transform.reader import TextReader
from example.transform.transformer import TextTransformer
from example.transform.types import TransformResult
from example.transform.writer import TextWriter


class TestTransformOrchestrator:
    """TransformOrchestratorクラスのテスト"""

    def test_orchestrate_正常系_複数行ファイルに行番号を付与(self, tmp_path: Path):
        # Arrange
        input_file = tmp_path / "input.txt"
        input_file.write_text("first line\nsecond line\nthird line", encoding="utf-8")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        context = TransformContext(
            target_file=input_file,
            tmp_dir=output_dir,
            current_datetime=datetime(2024, 12, 26, 15, 30, 45),
        )

        reader = TextReader(TextFileSystemReader())
        writer = TextWriter(TextFileSystemWriter())
        transformer = TextTransformer()
        orchestrator = TransformOrchestrator(reader=reader, transformer=transformer, writer=writer)

        # Act
        result = orchestrator.orchestrate(context)

        # Assert
        assert isinstance(result, TransformResult)
        assert result.length == 3

        output_file = output_dir / "input.txt"
        assert output_file.exists()

        content = output_file.read_text(encoding="utf-8")
        expected = "2024-12-26 15:30:45\n1: first line\n2: second line\n3: third line"
        assert content == expected

    def test_orchestrate_正常系_空ファイルは日時のみ(self, tmp_path: Path):
        # Arrange
        input_file = tmp_path / "empty.txt"
        input_file.write_text("", encoding="utf-8")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        context = TransformContext(
            target_file=input_file,
            tmp_dir=output_dir,
            current_datetime=datetime(2025, 1, 15, 10, 20, 30),
        )

        reader = TextReader(TextFileSystemReader())
        writer = TextWriter(TextFileSystemWriter())
        transformer = TextTransformer()
        orchestrator = TransformOrchestrator(reader=reader, transformer=transformer, writer=writer)

        # Act
        result = orchestrator.orchestrate(context)

        # Assert
        assert isinstance(result, TransformResult)
        assert result.length == 0

        output_file = output_dir / "empty.txt"
        assert output_file.exists()

        content = output_file.read_text(encoding="utf-8")
        expected = "2025-01-15 10:20:30"
        assert content == expected

    def test_orchestrate_正常系_単一行ファイルに行番号を付与(self, tmp_path: Path):
        # Arrange
        input_file = tmp_path / "single.txt"
        input_file.write_text("only one line", encoding="utf-8")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        context = TransformContext(
            target_file=input_file,
            tmp_dir=output_dir,
            current_datetime=datetime(2024, 6, 1, 8, 15, 0),
        )

        reader = TextReader(TextFileSystemReader())
        writer = TextWriter(TextFileSystemWriter())
        transformer = TextTransformer()
        orchestrator = TransformOrchestrator(reader=reader, transformer=transformer, writer=writer)

        # Act
        result = orchestrator.orchestrate(context)

        # Assert
        assert isinstance(result, TransformResult)
        assert result.length == 1

        output_file = output_dir / "single.txt"
        assert output_file.exists()

        content = output_file.read_text(encoding="utf-8")
        expected = "2024-06-01 08:15:00\n1: only one line"
        assert content == expected

    def test_orchestrate_正常系_日本語を含むファイル(self, tmp_path: Path):
        # Arrange
        input_file = tmp_path / "japanese.txt"
        input_file.write_text("これは1行目\nこれは2行目", encoding="utf-8")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        context = TransformContext(
            target_file=input_file,
            tmp_dir=output_dir,
            current_datetime=datetime(2024, 3, 20, 14, 30, 0),
        )

        reader = TextReader(TextFileSystemReader())
        writer = TextWriter(TextFileSystemWriter())
        transformer = TextTransformer()
        orchestrator = TransformOrchestrator(reader=reader, transformer=transformer, writer=writer)

        # Act
        result = orchestrator.orchestrate(context)

        # Assert
        assert isinstance(result, TransformResult)
        assert result.length == 2

        output_file = output_dir / "japanese.txt"
        assert output_file.exists()

        content = output_file.read_text(encoding="utf-8")
        expected = "2024-03-20 14:30:00\n1: これは1行目\n2: これは2行目"
        assert content == expected
