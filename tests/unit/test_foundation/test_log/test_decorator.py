"""@log デコレータのテスト"""

import logging

import pytest

from example.foundation.log.decorator import log


class TestLogDecorator:
    """@log デコレータのテスト"""

    def test_log_正常系_関数呼び出しと戻り値をログ出力する(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        # Arrange
        @log
        def sample_function(x: int, y: int) -> int:
            return x + y

        # Act
        with caplog.at_level(logging.INFO):
            result = sample_function(3, 5)

        # Assert
        assert result == 8
        assert len(caplog.records) > 0

    def test_log_正常系_メソッド呼び出しと戻り値をログ出力する(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        # Arrange
        class SampleClass:
            @log
            def sample_method(self, value: str) -> str:
                return f"processed: {value}"

        # Act
        with caplog.at_level(logging.INFO):
            obj = SampleClass()
            result = obj.sample_method("test")

        # Assert
        assert result == "processed: test"
        assert len(caplog.records) > 0

    def test_log_正常系_引数なし関数の呼び出しをログ出力する(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        # Arrange
        @log
        def no_arg_function() -> str:
            return "hello"

        # Act
        with caplog.at_level(logging.INFO):
            result = no_arg_function()

        # Assert
        assert result == "hello"
        assert len(caplog.records) > 0

    def test_log_異常系_例外を握り潰さずに再送出する(self) -> None:
        # Arrange
        @log
        def failing_function() -> None:
            raise ValueError("test error")

        # Act & Assert
        with pytest.raises(ValueError):
            failing_function()

    def test_log_正常系_デコレータ適用後も関数メタデータを保持する(self) -> None:
        # Arrange
        @log
        def documented_function(x: int) -> int:
            """This is a docstring"""
            return x * 2

        # Assert
        assert documented_function.__name__ == "documented_function"
        assert documented_function.__doc__ == "This is a docstring"

    def test_log_正常系_大きなリストを切り詰めること(self, caplog: pytest.LogCaptureFixture) -> None:
        @log
        def large_list_function() -> list[float]:
            return [0.1 * i for i in range(100)]

        with caplog.at_level(logging.INFO):
            result = large_list_function()

        assert len(result) == 100
        assert len(caplog.records) > 0

    def test_log_正常系_大きな辞書を切り詰めること(self, caplog: pytest.LogCaptureFixture) -> None:
        @log
        def large_dict_function() -> dict[str, int]:
            return {f"key_{i}": i for i in range(20)}

        with caplog.at_level(logging.INFO):
            result = large_dict_function()

        assert len(result) == 20
        assert len(caplog.records) > 0

    def test_log_正常系_長い文字列を切り詰めること(self, caplog: pytest.LogCaptureFixture) -> None:
        @log
        def long_string_function() -> str:
            return "a" * 200

        with caplog.at_level(logging.INFO):
            result = long_string_function()

        assert len(result) == 200
        assert len(caplog.records) > 0

    def test_log_正常系_小さなリストを切り詰めないこと(self, caplog: pytest.LogCaptureFixture) -> None:
        @log
        def small_list_function() -> list[int]:
            return [1, 2, 3]

        with caplog.at_level(logging.INFO):
            result = small_list_function()

        assert result == [1, 2, 3]
        assert len(caplog.records) > 0

    def test_log_正常系_小さな辞書を切り詰めないこと(self, caplog: pytest.LogCaptureFixture) -> None:
        @log
        def small_dict_function() -> dict[str, int]:
            return {"a": 1, "b": 2}

        with caplog.at_level(logging.INFO):
            result = small_dict_function()

        assert result == {"a": 1, "b": 2}
        assert len(caplog.records) > 0

    def test_log_正常系_大きなリスト引数を切り詰めること(self, caplog: pytest.LogCaptureFixture) -> None:
        @log
        def process_vector(vector: list[float]) -> int:
            return len(vector)

        large_vector = [0.1 * i for i in range(3072)]

        with caplog.at_level(logging.INFO):
            result = process_vector(large_vector)

        assert result == 3072
        assert len(caplog.records) > 0

    def test_log_正常系_空要素の大きな辞書を切り詰めること(self, caplog: pytest.LogCaptureFixture) -> None:
        # カスタム辞書クラス（len()は10以上、bool()はFalse）
        class FakeLargeEmptyDict(dict[str, int]):
            def __len__(self) -> int:
                return 10

            def __bool__(self) -> bool:
                return False

        @log
        def empty_dict_function() -> FakeLargeEmptyDict:
            return FakeLargeEmptyDict()

        with caplog.at_level(logging.INFO):
            result = empty_dict_function()

        assert len(result) == 10
        assert not result
        assert len(caplog.records) > 0
