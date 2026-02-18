"""example.foundation.error.ErrorHandler のテスト

エラーハンドラーのログ出力処理をテストします。
sys.exit は含まれず、エラーメッセージのログ出力のみを担当します。
"""

import pytest

from example.foundation.error import ApplicationError, ErrorHandler


class TestErrorHandler:
    """ErrorHandler クラスのテスト"""

    def test_handle_正常系_ApplicationError処理(self, caplog: pytest.LogCaptureFixture):
        # Arrange
        app_error = ApplicationError("ファイルが見つかりません")
        handler = ErrorHandler()

        # Act
        handler.handle(app_error)

        # Assert

        assert "type=example.foundation.error.error.ApplicationError" in caplog.text
        assert "message=ファイルが見つかりません" in caplog.text
        assert "cause_message=" in caplog.text

    def test_handle_正常系_ApplicationError処理_技術詳細あり(
        self, caplog: pytest.LogCaptureFixture
    ):
        # Arrange
        app_error = ApplicationError("API呼び出しに失敗しました", "Connection timeout after 30s")
        handler = ErrorHandler()

        # Act
        handler.handle(app_error)

        # Assert

        assert "type=example.foundation.error.error.ApplicationError" in caplog.text
        assert "message=API呼び出しに失敗しました" in caplog.text
        assert "cause_message=Connection timeout after 30s" in caplog.text

    def test_handle_正常系_Exception処理(self, caplog: pytest.LogCaptureFixture):
        # Arrange
        general_error = ValueError("Invalid input value")
        handler = ErrorHandler()

        # Act
        handler.handle(general_error)

        # Assert

        assert "type=builtins.ValueError" in caplog.text
        assert "message=Invalid input value" in caplog.text
        assert "cause_message=None" in caplog.text

    def test_handle_正常系_Exception処理_複雑な例外名(self, caplog: pytest.LogCaptureFixture):
        # Arrange
        complex_error = FileNotFoundError("/path/to/file.txt not found")
        handler = ErrorHandler()

        # Act
        handler.handle(complex_error)

        # Assert

        assert "type=builtins.FileNotFoundError" in caplog.text
        assert "message=/path/to/file.txt not found" in caplog.text
        assert "cause_message=None" in caplog.text
