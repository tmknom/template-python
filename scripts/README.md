# scripts

初期設定用のスクリプト群。

## 使い方

```bash
scripts/claude.sh
```

## 提供スクリプト

### claude.sh

Claude Code の初期設定を行うスクリプト。

- `.claude/` ディレクトリの作成
- `.claude/settings.local.json` の作成

### rename.sh

パッケージ名 `example` を新しいプロジェクト名に一括変換するスクリプト。

```bash
scripts/rename.sh <new_name>
```

- Python ソースコード・テストコードの import 文を更新
- `pyproject.toml`・`uv.lock` の設定を更新
- ドキュメント内のパッケージ名参照を更新
- `src/example/` ディレクトリをリネーム
