from pathlib import Path

import pytest

from example.config import AppConfig, EnvVarConfig


class TestAppConfig:
    """AppConfigクラスのテスト"""

    def test_build_正常系_EXAMPLE_TMP_DIR未設定時はcwd配下のtmpを使用(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ):
        # Arrange
        monkeypatch.delenv("EXAMPLE_TMP_DIR", raising=False)
        monkeypatch.chdir(tmp_path)

        # Act
        result = AppConfig.build(EnvVarConfig())

        # Assert
        assert result.tmp_dir == tmp_path / "tmp"

    def test_build_正常系_EXAMPLE_TMP_DIR設定時はその値を使用(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ):
        # Arrange
        monkeypatch.setenv("EXAMPLE_TMP_DIR", str(tmp_path / "custom"))

        # Act
        result = AppConfig.build(EnvVarConfig())

        # Assert
        assert result.tmp_dir == tmp_path / "custom"
