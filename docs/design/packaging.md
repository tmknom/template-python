# Pythonパッケージング設計ガイドライン

## 目的

このドキュメントは、Pythonパッケージの構成方針を定義する。
各方針を支えるツール設定については「推奨ツール設定」セクションを参照。

## テストディレクトリの `__init__.py`

### 原則: 作成しない

`tests/` 配下に `__init__.py` は作成しない。

### 理由

- pytestはテスト収集にパッケージ化を要求しない
- `__init__.py` があると `tests.*` という名前空間が成立し、意図しない import 経路が生まれる
- `tests.config` と `example.config` のような名前空間衝突のリスクがある
- 実行方法（`pytest` の実行ディレクトリ、`PYTHONPATH`、`-m pytest` 等）で挙動差が出やすくなる

### LLM による自動生成への対処

LLM（コード生成AI）が `tests/__init__.py` を自動生成する場合がある。
生成された場合は削除する。

相対 import のために `__init__.py` が必要と判断された場合でも、
`conftest.py` の fixture または `sys.path` 操作（テスト補助コードセクション参照）で解決する。

### テスト補助コード

テスト補助コード（ヘルパー、ファクトリーなど）は以下の方法で共有する。

#### 方針A（推奨）: conftest.py の fixture に集約

テスト補助ロジックは `conftest.py` に fixture として定義する。
補助コードが増えた場合も、まず fixture への集約を検討する。

#### 方針B: tests/ 直下にモジュールとして配置

fixture では扱いにくいユーティリティクラス等は `tests/` 直下にモジュールとして配置する。
`conftest.py` で `sys.path` に `tests/` ディレクトリを追加し、直接 import する。

```python
# tests/conftest.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
```

テストコードからは以下の形式で import する:

```python
from in_memory_fs import InMemoryWriter
```

Constraints:
    - テスト補助モジュールは `tests/` 直下にフラットに配置する
    - サブディレクトリ（`tests/helpers/` 等）は作成しない
    - ファイルが増えて散らかる場合は、fixture への集約を優先する

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
| `pythonpath` | `["src"]` | `tests` を含めず、テストコードのパッケージ化を防止 |
| `testpaths` | `["tests"]` | テスト検索パス（Python import パスではない） |

`pythonpath` は pytest 7.0+ のビルトイン機能であり、追加プラグインは不要。
プロジェクト標準は `pyproject.toml` の `[tool.pytest.ini_options]` セクションの設定を正とする。

`pythonpath` に `tests` を含めないことで、テストコード内での相対 import を防ぎ、`tests.*` という名前空間の成立を抑制する。これにより、上記「テストディレクトリの `__init__.py`」セクションで説明した名前空間衝突のリスクを回避できる。

### ruff（`__init__.py` 関連）

| 設定 | 値 | 対応する方針 |
|------|-----|-------------|
| `**/__init__.py` で `F401` 無視 | 未使用 import 許容 | 公開 API の re-export を許容 |
| `F401` を unfixable | 自動修正対象外 | re-export の誤削除を防止 |

### pyright

| 設定 | 値 | 対応する方針 |
|------|-----|-------------|
| `executionEnvironments` の `src` | `extraPaths = ["src"]` | プロダクションコードの import 解決 |
| `executionEnvironments` の `tests` | `extraPaths = ["src", "."]` | テストから src 配下と tests/ 直下のヘルパーモジュールにアクセス |

`extraPaths` の `"."` はプロジェクトルートを import パスに追加する設定である。
これにより `tests/` 直下に配置したヘルパーモジュールを pyright が解決できる。
ルート直下にプロダクション用モジュールは配置しないこと（プロダクションコードは `src/` 配下に限定する）。

### 設定ファイル

上記設定の実体は `pyproject.toml` の各ツールセクションにある。
