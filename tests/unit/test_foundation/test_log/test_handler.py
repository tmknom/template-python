"""example.foundation.log.handler のテスト"""

from pathlib import Path

import pytest

from example.foundation.log.handler import LogHandler


class TestLogHandler:
    """LogHandler クラスのテスト"""

    def setup_method(self):
        self._handler = LogHandler()

    @pytest.mark.parametrize(
        ("stream", "level", "expected_stream"),
        [
            ("stderr", "INFO", "ext://sys.stderr"),
            ("stdout", "DEBUG", "ext://sys.stdout"),
        ],
    )
    def test_create_console_handler_正常系_StreamHandlerの辞書を返す(
        self, stream: str, level: str, expected_stream: str
    ):
        # Arrange
        # Act
        result = self._handler.create_console_handler(stream=stream, level=level)

        # Assert
        assert result["class"] == "logging.StreamHandler"
        assert result["stream"] == expected_stream
        assert result["level"] == level
        assert result["formatter"] == "console"

    def test_create_file_handler_正常系_FileHandlerの辞書を返す(self):
        # Arrange
        log_path = Path("/tmp/test.log")

        # Act
        result = self._handler.create_file_handler(log_path)

        # Assert
        assert result["class"] == "logging.FileHandler"
        assert result["filename"] == str(log_path)
        assert result["encoding"] == "utf-8"
        assert result["level"] == "DEBUG"
        assert result["formatter"] == "file"
