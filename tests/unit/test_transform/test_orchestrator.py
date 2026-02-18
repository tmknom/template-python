from datetime import datetime
from pathlib import Path

from example.transform.context import TransformContext
from example.transform.orchestrator import TransformOrchestrator
from example.transform.reader import TextReader
from example.transform.transformer import TextTransformer
from example.transform.writer import TextWriter
from tests.unit.test_transform.fakes import InMemoryFsReader, InMemoryFsWriter


class TestTransformOrchestrator:
    """TransformOrchestratorクラスのテスト"""

    def _make_orchestrator(
        self,
        fs_reader: InMemoryFsReader,
        fs_writer: InMemoryFsWriter,
    ) -> TransformOrchestrator:
        return TransformOrchestrator(
            reader=TextReader(fs_reader),
            transformer=TextTransformer(),
            writer=TextWriter(fs_writer),
        )

    def _make_context(
        self, *, content: str = ""
    ) -> tuple[TransformContext, InMemoryFsReader, InMemoryFsWriter]:
        fs_reader = InMemoryFsReader(content=content)
        fs_writer = InMemoryFsWriter()
        context = TransformContext(
            target_file=Path("input.txt"),
            tmp_dir=Path("/tmp/output"),
            current_datetime=datetime(2024, 12, 26, 15, 30, 45),
        )
        return context, fs_reader, fs_writer

    def test_orchestrate_正常系_target_fileを読み込んで変換結果を書き込むこと(self):
        # Arrange
        context, fs_reader, fs_writer = self._make_context(content="line1\nline2\nline3")
        orchestrator = self._make_orchestrator(fs_reader, fs_writer)

        # Act
        result = orchestrator.orchestrate(context)

        # Assert
        assert fs_reader.read_path == context.target_file
        assert fs_writer.written_path == context.tmp_dir / context.target_file.name
        assert fs_writer.written_text is not None
        first_line = fs_writer.written_text.splitlines()[0]
        assert first_line == "2024-12-26 15:30:45"
        assert "line1" in fs_writer.written_text
        assert "line2" in fs_writer.written_text
        assert "line3" in fs_writer.written_text
        assert result.length == 3
