from example.transform.types import TransformResult


class TestTransformResult:
    """TransformResultクラスのテスト"""

    def test_init_正常系_length属性が正しく保持されること(self):
        # Arrange & Act
        result = TransformResult(length=42)

        # Assert
        assert result.length == 42
