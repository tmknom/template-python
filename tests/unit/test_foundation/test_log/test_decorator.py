"""@log デコレータのテスト"""

import logging

import pytest

from example.foundation.log.decorator import log


class TestLogDecorator:
    """@log デコレータのテスト"""

    def test_log_function_call_and_return(self, caplog: pytest.LogCaptureFixture) -> None:
        @log
        def sample_function(x: int, y: int) -> int:
            return x + y

        with caplog.at_level(logging.INFO):
            result = sample_function(3, 5)

        assert result == 8
        assert "sample_function" in caplog.text
        assert "sample_function(3, 5)" in caplog.text
        assert "sample_function returned: 8" in caplog.text

    def test_log_method_call_and_return(self, caplog: pytest.LogCaptureFixture) -> None:
        class SampleClass:
            @log
            def sample_method(self, value: str) -> str:
                return f"processed: {value}"

        with caplog.at_level(logging.INFO):
            obj = SampleClass()
            result = obj.sample_method("test")

        assert result == "processed: test"
        assert "sample_method" in caplog.text
        assert "SampleClass.sample_method('test')" in caplog.text
        assert "SampleClass.sample_method returned: 'processed: test'" in caplog.text

    def test_log_with_no_arguments(self, caplog: pytest.LogCaptureFixture) -> None:
        @log
        def no_arg_function() -> str:
            return "hello"

        with caplog.at_level(logging.INFO):
            result = no_arg_function()

        assert result == "hello"
        assert "no_arg_function" in caplog.text
        assert "no_arg_function()" in caplog.text

    def test_log_does_not_suppress_exception(self) -> None:
        """例外が発生した場合、そのまま再送出されること（ログ出力なし）"""

        @log
        def failing_function() -> None:
            raise ValueError("test error")

        with pytest.raises(ValueError, match="test error"):
            failing_function()

    def test_log_preserves_function_metadata(self) -> None:
        @log
        def documented_function(x: int) -> int:
            """This is a docstring"""
            return x * 2

        assert documented_function.__name__ == "documented_function"
        assert documented_function.__doc__ == "This is a docstring"

    def test_log_truncates_large_list(self, caplog: pytest.LogCaptureFixture) -> None:
        @log
        def large_list_function() -> list[float]:
            return [0.1 * i for i in range(100)]

        with caplog.at_level(logging.INFO):
            result = large_list_function()

        assert len(result) == 100
        assert "large_list_function" in caplog.text
        assert "large_list_function returned: [0.0, ... (100 items)]" in caplog.text

    def test_log_truncates_large_dict(self, caplog: pytest.LogCaptureFixture) -> None:
        @log
        def large_dict_function() -> dict[str, int]:
            return {f"key_{i}": i for i in range(20)}

        with caplog.at_level(logging.INFO):
            result = large_dict_function()

        assert len(result) == 20
        assert "large_dict_function" in caplog.text
        assert "large_dict_function returned: {'key_0': 0, ... (20 keys)}" in caplog.text

    def test_log_truncates_long_string(self, caplog: pytest.LogCaptureFixture) -> None:
        @log
        def long_string_function() -> str:
            return "a" * 200

        with caplog.at_level(logging.INFO):
            result = long_string_function()

        assert len(result) == 200
        assert "long_string_function" in caplog.text
        assert '... (200 chars)"' in caplog.text

    def test_log_does_not_truncate_small_list(self, caplog: pytest.LogCaptureFixture) -> None:
        @log
        def small_list_function() -> list[int]:
            return [1, 2, 3]

        with caplog.at_level(logging.INFO):
            result = small_list_function()

        assert result == [1, 2, 3]
        assert "small_list_function" in caplog.text
        assert "small_list_function returned: [1, 2, 3]" in caplog.text

    def test_log_does_not_truncate_small_dict(self, caplog: pytest.LogCaptureFixture) -> None:
        @log
        def small_dict_function() -> dict[str, int]:
            return {"a": 1, "b": 2}

        with caplog.at_level(logging.INFO):
            result = small_dict_function()

        assert result == {"a": 1, "b": 2}
        assert "small_dict_function" in caplog.text
        assert "small_dict_function returned: {'a': 1, 'b': 2}" in caplog.text

    def test_log_truncates_large_list_argument(self, caplog: pytest.LogCaptureFixture) -> None:
        @log
        def process_vector(vector: list[float]) -> int:
            return len(vector)

        large_vector = [0.1 * i for i in range(3072)]

        with caplog.at_level(logging.INFO):
            result = process_vector(large_vector)

        assert result == 3072
        assert "process_vector" in caplog.text
        assert "process_vector([0.0, ... (3072 items)])" in caplog.text

    def test_log_truncates_empty_large_dict(self, caplog: pytest.LogCaptureFixture) -> None:
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
        assert "empty_dict_function" in caplog.text
        assert "{... (0 keys)}" in caplog.text
