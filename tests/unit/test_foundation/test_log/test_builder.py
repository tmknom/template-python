"""example.foundation.log.builder のテスト"""

import logging
from pathlib import Path

from example.foundation.log.builder import LogDictConfigBuilder


class TestLogDictConfigBuilder:
    """LogDictConfigBuilder クラスのテスト"""

    def setup_method(self):
        self._builder = LogDictConfigBuilder()

    def test_build_正常系_コンソールのみの設定を返す(self):
        # Act
        result = self._builder.build(
            level="INFO",
            stream="stdout",
            file_output=False,
            log_path=None,
            console_formatter_type="json_context",
        )

        # Assert
        assert result["version"] == 1
        assert "console" in result["handlers"]
        assert "file" not in result["handlers"]
        assert result["root"]["handlers"] == ["console"]

    def test_build_正常系_ファイルハンドラーを含む設定を返す(self):
        # Act
        log_path = Path("/tmp/test.log")
        result = self._builder.build(
            level="DEBUG",
            stream="stderr",
            file_output=True,
            log_path=log_path,
            console_formatter_type="color",
        )

        # Assert
        assert "file" in result["handlers"]
        assert "file" in result["root"]["handlers"]
        assert "file" in result["formatters"]

    def test_build_正常系_JSONフォーマッタークラスを含む設定を返す(self):
        # Act
        class CustomFormatter(logging.Formatter):
            pass

        result = self._builder.build(
            level="INFO",
            stream="stdout",
            file_output=False,
            log_path=None,
            console_formatter_type="json_context",
            json_formatter_class=CustomFormatter,
        )

        # Assert
        assert result["formatters"]["console"]["()"] is CustomFormatter

    def test_build_正常系_disable_existing_loggers_falseの設定を返す(self):
        # Act
        result = self._builder.build(
            level="INFO",
            stream="stdout",
            file_output=False,
            log_path=None,
            console_formatter_type="json_context",
        )

        # Assert
        assert result["disable_existing_loggers"] is False
