from datetime import datetime
from pathlib import Path

from example.transform.context import TransformContext
from example.transform.orchestrator import TransformOrchestrator
from example.transform.reader import TextReader
from example.transform.transformer import TextTransformer
from example.transform.writer import TextWriter
from tests.fake import InMemoryFsReader, InMemoryFsWriter


class TestTransformOrchestrator:
    """TransformOrchestratorクラスのテスト"""

    def test_orchestrate_正常系_target_fileを読み込んで変換結果を書き込むこと(self):
        # Arrange
        fs_reader = InMemoryFsReader(contents={"input.txt": "line1\nline2\nline3"})
        fs_writer = InMemoryFsWriter()
        orchestrator = TransformOrchestrator(
            reader=TextReader(fs_reader),
            transformer=TextTransformer(),
            writer=TextWriter(fs_writer),
        )
        context = TransformContext(
            target_file=Path("input.txt"),
            tmp_dir=Path("/tmp/output"),
            current_datetime=datetime(2024, 12, 26, 15, 30, 45),
        )

        # Act
        result = orchestrator.orchestrate(context)

        # Assert
        assert result.src_length == 3
        assert result.dst_length == 4
        assert "/tmp/output/input.txt" in fs_writer.written
