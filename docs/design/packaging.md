# Pythonパッケージング設計ガイドライン

## 目的

このドキュメントは、Pythonパッケージの構成方針を定義する。
各方針を支えるツール設定については「推奨ツール設定」セクションを参照。

## テストディレクトリの `__init__.py`

### 原則: 空ファイルで配置する

`tests/` 配下に `__init__.py` は空ファイル（コメントなし、docstringなし）で配置する。

### 理由

- パッケージ固有の Fake・補助クラスをサブディレクトリに配置し、絶対 import で参照できる
- `sys.path` 操作や `conftest.py` への fixture 集約が不要になる
- 絶対 import により、どのパッケージの補助コードかが明確になる

### テスト補助コード（Fake クラス）

テスト補助コード（InMemory 実装など）は対象パッケージのテストディレクトリに配置する。

#### 方針A（推奨）: パッケージ専用の fakes.py に集約

Protocol 準拠の InMemory 実装は、各テストパッケージの `fakes.py` に定義する。
`__init__.py` によるパッケージ化と `pythonpath` へのプロジェクトルート追加により、絶対 import で参照できる。

```python
# tests/unit/test_transform/fakes.py
from pathlib import Path

class InMemoryFsReader:
    def __init__(self, content: str = ""):
        self.content = content
        self.read_path: Path | None = None

    def read(self, file_path: Path) -> str:
        self.read_path = file_path
        return self.content
```

テストコードからは以下の形式で import する:

```python
from tests.unit.test_transform.fakes import InMemoryFsReader
```

Constraints:
    - `fakes.py` はパッケージ専用とし、他パッケージと共有しない
    - 共有が必要になった場合は設計を見直す

#### 方針B: conftest.py の fixture に集約

テスト全体で共有する補助ロジックは `conftest.py` に fixture として定義する。

## プロダクションコードの `__init__.py`

### 原則: 必須

プロダクションコードでは `__init__.py` は必須。
docstring方針は [comment.md](comment.md) を参照。

本プロジェクトでは公開API境界を `__all__` で明示するため、namespace package（`__init__.py` なしのパッケージ）は採用しない。
すべてのプロダクションパッケージに `__init__.py` を配置する。

### re-export

`__init__.py` で内部モジュールを re-export し、パッケージの公開APIを定義する。
`__all__` に列挙したもののみ互換性対象とする。

## 推奨ツール設定

本ドキュメントの方針を支える `pyproject.toml` 設定。

### pytest

| 設定 | 値 | 対応する方針 |
|------|-----|-------------|
| `pythonpath` | `["src", "."]` | `src/` 配下と `tests/` 配下を絶対 import で参照できるようにする |
| `testpaths` | `["tests"]` | テスト検索パス（Python import パスではない） |

`pythonpath` は pytest 7.0+ のビルトイン機能であり、追加プラグインは不要。
プロジェクト標準は `pyproject.toml` の `[tool.pytest.ini_options]` セクションの設定を正とする。

`"."` （プロジェクトルート）を `pythonpath` に追加することで、`tests.unit.test_transform.fakes` のような絶対 import が解決できる。
`__init__.py` によりテストディレクトリがパッケージとして認識されるため、各 `fakes.py` を絶対パスで参照できる。

### ruff（`__init__.py` 関連）

| 設定 | 値 | 対応する方針 |
|------|-----|-------------|
| `**/__init__.py` で `F401` 無視 | 未使用 import 許容 | 公開 API の re-export を許容 |
| `F401` を unfixable | 自動修正対象外 | re-export の誤削除を防止 |

### pyright

| 設定 | 値 | 対応する方針 |
|------|-----|-------------|
| `executionEnvironments` の `src` | `extraPaths = ["src"]` | プロダクションコードの import 解決 |
| `executionEnvironments` の `tests` | `extraPaths = ["src", "."]` | テストから src 配下にアクセス |

`__init__.py` によるパッケージ化と `"."` の追加により、テストパッケージの絶対 import は pyright が解決する。
`"."` はプロジェクトルートを import パスに追加する設定であり、pytest の `pythonpath` 設定と対応する。
ルート直下にプロダクション用モジュールは配置しないこと（プロダクションコードは `src/` 配下に限定する）。

### 設定ファイル

上記設定の実体は `pyproject.toml` の各ツールセクションにある。
