"""統合CLIツールの統合テスト

CLIの共通動作を検証
"""

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def tmp_dir(tmp_path: Path) -> Path:
    """統合テスト用ワークスペース"""
    test_dir = tmp_path / "integration_test"
    test_dir.mkdir()
    return test_dir


class TestIntegrationCLI:
    """統合テスト"""

    def test_サブコマンド未指定_ヘルプ表示(self, tmp_dir: Path):
        cmd = [sys.executable, "-m", "example.cli"]
        result = subprocess.run(cmd, cwd=tmp_dir, capture_output=True, text=True, timeout=10)

        # Typerはno_args_is_help=True設定時、ヘルプを表示してexit code 2を返す
        assert result.returncode == 2
        assert "Usage:" in result.stdout

    def test_helpオプション_ヘルプ表示(self, tmp_dir: Path):
        cmd = [sys.executable, "-m", "example.cli", "--help"]
        result = subprocess.run(cmd, cwd=tmp_dir, capture_output=True, text=True, timeout=10)

        # ヘルプ表示は成功として扱われる
        assert result.returncode == 0
        assert "Usage:" in result.stdout

    def test_transform_正常系_ファイル変換を実行(self, tmp_dir: Path):
        # Arrange
        input_file = tmp_dir / "input.txt"
        input_file.write_text("test line", encoding="utf-8")
        tmp_output_dir = tmp_dir / "tmp"
        tmp_output_dir.mkdir()

        # Act
        cmd = [sys.executable, "-m", "example.cli", "transform", str(input_file)]
        result = subprocess.run(cmd, cwd=tmp_dir, capture_output=True, text=True, timeout=10)

        # Assert
        assert result.returncode == 0
        assert "TransformResult" in result.stdout
        assert "length=" in result.stdout

        # 出力ファイルが作成されていることを確認
        output_file = tmp_output_dir / "input.txt"
        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert "1: test line" in content

    def test_transform_異常系_存在しないファイル(self, tmp_dir: Path):
        # Arrange
        non_existent_file = tmp_dir / "non_existent.txt"

        # Act
        cmd = [sys.executable, "-m", "example.cli", "transform", str(non_existent_file)]
        result = subprocess.run(cmd, cwd=tmp_dir, capture_output=True, text=True, timeout=10)

        # Assert
        assert result.returncode == 1
        # エラーメッセージが出力されることを確認（標準エラー出力に表示される）
        assert result.stderr or "Error" in result.stdout
