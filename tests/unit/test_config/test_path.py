from pathlib import Path

from example.config import PathConfig


class TestPathConfig:
    def test_from_base_dir_正常系_tmpディレクトリを生成(self, tmp_path: Path):
        # Act
        result = PathConfig.from_base_dir(tmp_path)

        # Assert
        assert isinstance(result, PathConfig)
        assert result.tmp_dir == tmp_path / "tmp"
