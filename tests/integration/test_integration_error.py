import subprocess
import sys
from pathlib import Path


class TestIntegrationError:
    """ErrorHandlerのインテグレーションテスト

    main() の ErrorHandler が例外を捕捉して sys.exit(1) に変換する経路を検証する。
    未知のサブコマンドでは Typer が先に exit code 2 で終了し ErrorHandler に到達しないため、
    実在するサブコマンド経由で例外を発生させる必要がある。
    使用するサブコマンド自体のロジックは、このテストの関心事ではない。
    """

    def test_例外発生時_ErrorHandlerがexit_code_1で終了すること(self, tmp_dir: Path):
        # Arrange
        non_existent_file = tmp_dir / "non_existent.txt"

        # Act
        cmd = [sys.executable, "-m", "example.cli", "transform", str(non_existent_file)]
        result = subprocess.run(cmd, cwd=tmp_dir, capture_output=True, text=True, timeout=10)

        # Assert
        assert result.returncode == 1
