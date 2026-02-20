from example.transform.types import DstText, SrcText


class TestSrcText:
    """SrcTextクラスのテスト"""

    def test_numbered_lines_正常系_複数行テキストに行番号を付与(self):
        # Arrange
        src = SrcText("first\nsecond\nthird")

        # Act
        result = src.numbered_lines()

        # Assert
        assert result == ["1: first", "2: second", "3: third"]

    def test_numbered_lines_正常系_空テキストは空リストを返す(self):
        # Arrange
        src = SrcText("")

        # Act
        result = src.numbered_lines()

        # Assert
        assert result == []

    def test_length_正常系_行数を返す(self):
        # Arrange
        src = SrcText("line1\nline2\nline3")

        # Act
        result = src.length()

        # Assert
        assert result == 3


class TestDstText:
    """DstTextクラスのテスト"""

    def test_length_正常系_行数を返す(self):
        # Arrange
        dst = DstText("line1\nline2\nline3")

        # Act
        result = dst.length()

        # Assert
        assert result == 3

    def test_str_正常系_内部テキストを文字列として返す(self):
        # Arrange
        dst = DstText("hello\nworld")

        # Act
        result = str(dst)

        # Assert
        assert result == "hello\nworld"
