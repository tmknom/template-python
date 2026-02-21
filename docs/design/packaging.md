# Pythonパッケージング設計ガイドライン

## 目的

このドキュメントは、Pythonパッケージの構成方針を定義する。

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

## ツール設定

本ドキュメントの方針に対応する `pyproject.toml` の設定内容（`pythonpath`、`executionEnvironments`、`F401` の per-file-ignores など）は別ドキュメントに集約している。
