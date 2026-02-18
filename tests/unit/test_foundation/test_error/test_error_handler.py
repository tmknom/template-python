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
        handler = ErrorHandler(app_error)

        # Act
        handler.handle()

        # Assert

        assert "type=example.foundation.error.error.ApplicationError" in caplog.text
        assert "message=ファイルが見つかりません" in caplog.text
        assert "cause_message=" in caplog.text

    def test_handle_正常系_ApplicationError処理_技術詳細あり(
        self, caplog: pytest.LogCaptureFixture
    ):
        # Arrange
        app_error = ApplicationError("API呼び出しに失敗しました", "Connection timeout after 30s")
        handler = ErrorHandler(app_error)

        # Act
        handler.handle()

        # Assert

        assert "type=example.foundation.error.error.ApplicationError" in caplog.text
        assert "message=API呼び出しに失敗しました" in caplog.text
        assert "cause_message=Connection timeout after 30s" in caplog.text

    def test_handle_正常系_Exception処理(self, caplog: pytest.LogCaptureFixture):
        # Arrange
        general_error = ValueError("Invalid input value")
        handler = ErrorHandler(general_error)

        # Act
        handler.handle()

        # Assert

        assert "type=builtins.ValueError" in caplog.text
        assert "message=Invalid input value" in caplog.text
        assert "cause_message=None" in caplog.text

    def test_handle_正常系_Exception処理_複雑な例外名(self, caplog: pytest.LogCaptureFixture):
        # Arrange
        complex_error = FileNotFoundError("/path/to/file.txt not found")
        handler = ErrorHandler(complex_error)

        # Act
        handler.handle()

        # Assert

        assert "type=builtins.FileNotFoundError" in caplog.text
        assert "message=/path/to/file.txt not found" in caplog.text
        assert "cause_message=None" in caplog.text

    def test_handle_正常系_ログレベルERROR指定(self, caplog: pytest.LogCaptureFixture):
        # Arrange
        import logging

        app_error = ApplicationError("重大なエラーが発生しました")
        handler = ErrorHandler(app_error, log_level=logging.ERROR)

        # Act
        handler.handle()

        # Assert

        assert "重大なエラーが発生しました" in caplog.text
        # ERRORレベルで出力されたことを確認
        assert any(record.levelname == "ERROR" for record in caplog.records)

    def test_handle_正常系_ログレベルWARNING指定(self, caplog: pytest.LogCaptureFixture):
        # Arrange
        import logging

        app_error = ApplicationError("警告レベルのエラーです")
        handler = ErrorHandler(app_error, log_level=logging.WARNING)

        # Act
        handler.handle()

        # Assert

        assert "警告レベルのエラーです" in caplog.text
        # WARNINGレベルで出力されたことを確認
        assert any(record.levelname == "WARNING" for record in caplog.records)

    def test_handle_正常系_ログレベルINFO指定(self, caplog: pytest.LogCaptureFixture):
        # Arrange
        import logging

        # caplogのレベルをINFOに設定
        caplog.set_level(logging.INFO)

        app_error = ApplicationError("情報レベルのエラーです")
        handler = ErrorHandler(app_error, log_level=logging.INFO)

        # Act
        handler.handle()

        # Assert

        assert "情報レベルのエラーです" in caplog.text
        # INFOレベルで出力されたことを確認
        assert any(record.levelname == "INFO" for record in caplog.records)

    def test_handle_正常系_コンテキスト情報付き(self, caplog: pytest.LogCaptureFixture):
        # Arrange
        app_error = ApplicationError("エラーが発生しました")
        context = {
            "request_id": "req_123456",
            "http_method": "POST",
            "endpoint": "/api/search",
            "error_category": "application_error",
        }
        handler = ErrorHandler(app_error, context=context)

        # Act
        handler.handle()

        # Assert

        assert "エラーが発生しました" in caplog.text
        assert "request_id=req_123456" in caplog.text
        assert "http_method=POST" in caplog.text
        assert "endpoint=/api/search" in caplog.text
        assert "error_category=application_error" in caplog.text

    def test_handle_正常系_コンテキスト情報なし(self, caplog: pytest.LogCaptureFixture):
        # Arrange
        app_error = ApplicationError("エラーが発生しました")
        handler = ErrorHandler(app_error, context=None)

        # Act
        handler.handle()

        # Assert

        assert "エラーが発生しました" in caplog.text
        # contextフィールドが出力されないことを確認
        assert "request_id=" not in caplog.text

    def test_handle_正常系_ログレベルとコンテキスト両方指定(self, caplog: pytest.LogCaptureFixture):
        # Arrange
        import logging

        app_error = ApplicationError("警告レベルのエラーです")
        context = {
            "request_id": "req_789",
            "error_category": "client_error",
        }
        handler = ErrorHandler(app_error, log_level=logging.WARNING, context=context)

        # Act
        handler.handle()

        # Assert

        assert "警告レベルのエラーです" in caplog.text
        assert any(record.levelname == "WARNING" for record in caplog.records)
        assert "request_id=req_789" in caplog.text
        assert "error_category=client_error" in caplog.text
