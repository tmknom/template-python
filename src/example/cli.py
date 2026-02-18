#!/usr/bin/env python3
"""CLIツールのエントリーポイント

uv run コマンド経由での実行を想定している。
サブコマンドの実装には Typer を使い、一貫性のある体験を提供する。
各サブコマンドを定義しているメソッドでは、次の処理を実行する。

- Config から環境設定を取得し、 Context へ実行時の動的パラメータをセット
- OrchestratorProviderで静的な依存グラフを解決し、Orchestrator をインスタンス化
- Orchestrator がサブコマンドのビジネスロジックを実行

本ファイルにはビジネスロジックは持たせない。
依存するコンポーネントを適切に組み立て、Orchestrator を実行することが責務である。
なおエラー発生時は main 関数内の ErrorHandler が例外を補足し、エラーハンドリングを実行する。

Usage:
    uv run example transform xxxx.md
    uv run example --help
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer

from example.config import PathConfig
from example.foundation.error import ErrorHandler
from example.foundation.log import LogConfigurator
from example.transform import TransformContext, TransformOrchestratorProvider

logger = logging.getLogger(__name__)
app = typer.Typer(no_args_is_help=True)


@app.callback()
def main_callback(ctx: typer.Context) -> None:
    """各コマンドの共通処理"""
    app_name = ctx.invoked_subcommand or "example"
    log_configurator = LogConfigurator(app_name=app_name, level="INFO")
    log_path = log_configurator.configure_plain()
    logger.info("Starting %s command; log file: %s", app_name, log_path)


@app.command()
def transform(
    target_file: Annotated[Path, typer.Argument(help="ファイルパス")],
) -> None:
    """テキストファイルを読み込み、行番号を付与して出力"""
    path_config = PathConfig.from_base_dir(Path.cwd())
    context = TransformContext(
        target_file=target_file,
        tmp_dir=path_config.tmp_dir,
        current_datetime=datetime.now(),
    )
    orchestrator = TransformOrchestratorProvider().provide()
    result = orchestrator.orchestrate(context)
    print(result)


def main() -> None:
    """メイン関数"""
    try:
        app()
    except Exception as e:
        ErrorHandler().handle(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
