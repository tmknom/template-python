from datetime import datetime

from example.transform.transformer import TextTransformer
from example.transform.types import SrcText


class TestTextTransformer:
    """TextTransformerクラスのテスト"""

    def test_transform_正常系_複数行テキストに行番号を付与(self):
        # Arrange
        text = SrcText("first\nsecond\nthird")
        current_datetime = datetime(2026, 2, 18, 12, 0, 0)
        transformer = TextTransformer()

        # Act
        result = transformer.transform(text, current_datetime)

        # Assert
        expected = "2026-02-18 12:00:00\n1: first\n2: second\n3: third"
        assert result == expected

    def test_transform_正常系_空テキストは日時のみ(self):
        # Arrange
        text = SrcText("")
        current_datetime = datetime(2026, 2, 18, 12, 0, 0)
        transformer = TextTransformer()

        # Act
        result = transformer.transform(text, current_datetime)

        # Assert
        expected = "2026-02-18 12:00:00"
        assert result == expected

    def test_transform_正常系_単一行テキストに行番号を付与(self):
        # Arrange
        text = SrcText("only one line")
        current_datetime = datetime(2026, 2, 18, 9, 30, 0)
        transformer = TextTransformer()

        # Act
        result = transformer.transform(text, current_datetime)

        # Assert
        expected = "2026-02-18 09:30:00\n1: only one line"
        assert result == expected

    def test_transform_正常系_日本語テキストに行番号を付与(self):
        # Arrange
        text = SrcText("こんにちは\n世界")
        current_datetime = datetime(2026, 2, 18, 0, 0, 0)
        transformer = TextTransformer()

        # Act
        result = transformer.transform(text, current_datetime)

        # Assert
        expected = "2026-02-18 00:00:00\n1: こんにちは\n2: 世界"
        assert result == expected
