"""example.foundation.log.configurator のテスト

ログ設定機能のテストを実装します。
"""

import logging
from collections.abc import Callable
from typing import Any

from example.foundation.log.configurator import LogConfigurator


class TestLogConfigurator:
    """LogConfigurator クラスのテスト"""

    def setup_method(self):
        """各テストメソッド実行前のセットアップ"""
        self.cleanup_logger()

    def teardown_method(self):
        """各テストメソッド実行後のクリーンアップ"""
        self.cleanup_logger()

    def cleanup_logger(self):
        """ロガーのクリーンアップ"""
        # ルートロガーのハンドラーをクリア
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
        # ロガーのレベルをリセット
        logger.setLevel(logging.NOTSET)

    def with_clean_logger(self, func: Callable[[], Any]) -> Any:
        """pytestハンドラーを一時的に削除してテストを実行"""
        logger = logging.getLogger()
        pytest_handlers = logger.handlers[:]
        for handler in pytest_handlers:
            logger.removeHandler(handler)

        try:
            return func()
        finally:
            # pytestハンドラーを復元
            for handler in pytest_handlers:
                logger.addHandler(handler)

    def test_configure_plain_正常系_ハンドラー設定確認(self):
        def test_func():
            configurator = LogConfigurator(app_name="test_app", level="INFO")
            configurator.configure_plain()

            # ハンドラーが設定されていることを確認
            logger = logging.getLogger()
            assert len(logger.handlers) == 2

            # ConsoleHandlerとFileHandlerが存在することを確認
            console_handler: logging.StreamHandler[Any] | None = next(  # pyright: ignore[reportUnknownVariableType]
                (  # pyright: ignore[reportUnknownArgumentType]
                    h
                    for h in logger.handlers
                    if isinstance(h, logging.StreamHandler)
                    and not isinstance(h, logging.FileHandler)
                ),
                None,
            )
            file_handler: logging.FileHandler | None = next(
                (h for h in logger.handlers if isinstance(h, logging.FileHandler)),
                None,
            )

            assert console_handler is not None
            assert file_handler is not None

            # ConsoleHandlerのレベル確認
            assert console_handler.level == logging.INFO

            # FileHandlerのレベル確認
            assert file_handler.level == logging.DEBUG

        self.with_clean_logger(test_func)

    def test_configure_plain_正常系_再初期化防止(self):
        def test_func():
            configurator = LogConfigurator(app_name="test_app", level="INFO")
            log_path_1 = configurator.configure_plain()

            # 2回目の初期化
            configurator2 = LogConfigurator(app_name="different_app", level="DEBUG")
            log_path_2 = configurator2.configure_plain()

            # 再初期化が防止され、既存のFileHandlerのパスまたはNoneが返却される
            # log_path_1 が None でなければ、log_path_2 も同じパスを返すか None を返す
            if log_path_1 is not None:
                assert log_path_2 == log_path_1 or log_path_2 is None
            else:
                assert log_path_2 is None

        self.with_clean_logger(test_func)

    def test_configure_json_正常系_ハンドラー設定確認(self):
        def test_func():
            configurator = LogConfigurator(app_name="test_app", level="DEBUG")
            log_path = configurator.configure_json()

            # ファイル出力なしのためNoneが返却される
            assert log_path is None

            # ハンドラーが設定されていることを確認(コンソールのみ)
            logger = logging.getLogger()
            assert len(logger.handlers) == 1

            # ConsoleHandlerが存在することを確認
            console_handler: logging.StreamHandler[Any] | None = next(  # pyright: ignore[reportUnknownVariableType]
                (  # pyright: ignore[reportUnknownArgumentType]
                    h
                    for h in logger.handlers
                    if isinstance(h, logging.StreamHandler)
                    and not isinstance(h, logging.FileHandler)
                ),
                None,
            )

            assert console_handler is not None
            assert console_handler.level == logging.DEBUG

        self.with_clean_logger(test_func)

    def test_configure_正常系_再初期化時にFileHandlerがない場合Noneを返す(self):
        def test_func():
            # 最初にコンソールハンドラーのみを設定
            logger = logging.getLogger()
            console_handler = logging.StreamHandler()
            logger.addHandler(console_handler)

            # 再初期化を試みる
            configurator = LogConfigurator(app_name="test_app", level="INFO")
            log_path = configurator.configure_plain()

            # FileHandlerがないためNoneが返る
            assert log_path is None

        self.with_clean_logger(test_func)

    def test_configure_json_with_custom_formatter_正常系_カスタムフォーマッターを使用(self):
        def test_func():
            # カスタムフォーマッタークラスを定義
            class CustomFormatter(logging.Formatter):
                def format(self, record: logging.LogRecord) -> str:
                    return f"CUSTOM: {record.getMessage()}"

            configurator = LogConfigurator(app_name="test_app", level="DEBUG")
            log_path = configurator._configure(  # pyright: ignore[reportPrivateUsage]
                stream="stdout",
                file_output=False,
                console_formatter_type="json_context",
                file_formatter_type="",
                json_formatter_class=CustomFormatter,
            )

            # ファイル出力なしのためNoneが返却される
            assert log_path is None

            # ハンドラーが設定されていることを確認
            logger = logging.getLogger()
            assert len(logger.handlers) == 1

        self.with_clean_logger(test_func)
