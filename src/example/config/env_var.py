"""Configパッケージの環境変数設定モジュール

実行環境から注入される環境変数を扱う。
"""

from pathlib import Path
from typing import Literal

from example.foundation.model import CoreSettings, SettingsConfigDict

LogLevel = Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]


class EnvVarConfig(CoreSettings):
    """環境変数から設定値を読み込む不変データコンテナ

    EXAMPLE_ プレフィックスの環境変数を自動マッピングする。
    未設定項目はデフォルト値を使用し、未知の環境変数は禁止する。
    """

    model_config = SettingsConfigDict(
        env_prefix="EXAMPLE_",
    )

    log_level: LogLevel = "INFO"
    tmp_dir: Path | None = None
