# Pythonコメント設計ガイドライン

## 目的

このドキュメントは、Pythonコードにおけるdocstringとインラインコメントの書き方を定義する。

既存の設計原則である [python-design-principles.md](python-design-principles.md) では「Google形式でdocstringを記述」という方針を定めているが、モジュールdocstringとクラスdocstringの書き分け方や、インラインコメントの指針は未定義であった。本ドキュメントでその不足を補完する。

## docstring

### 書く場所ごとの役割

| 場所 | 役割 | 記述内容 |
|------|------|----------|
| モジュールdocstring | 設計上の位置づけ | ・アーキテクチャ上の責務<br>・依存方向（層としての関係）<br>・前提条件や制約 |
| クラスdocstring | 具体的な責務・仕様 | ・クラスの主な機能<br>・処理フロー、ライフサイクル<br>・入出力の契約、制約 |
| メソッドdocstring | 引数・戻り値・例外 | ・型アノテーションとArgs/Returns/Raisesで十分なら省略可<br>・複雑なロジックや副作用がある場合は詳細を記述 |

**原則**: モジュールは「層としての依存方向と設計判断」を示し、クラスは「何をどう行うか」を示す。具体的なクラス名や呼び出し元の列挙は避ける。

### セクション名は英語で記述

Google Styleの標準セクション（Args, Returns, Raises, Attributesなど）に合わせ、独自セクションも英語で記述する。

**推奨セクション名（設計意図を記述するもの）**:

| セクション名 | 用途 | 記述すべき内容 |
|-------------|------|---------------|
| Flow | 処理フロー | なぜこの順序か、ステップの意図 |
| Lifecycle | ライフサイクル | いつ生成され、いつまで有効か |
| Constraints | 制約 | してはいけないこと、前提条件、設計判断 |
| Scope | スコープ | 適用範囲、どのレイヤーで使うか |
| Configuration | 設定 | 設定値の意味と効果、なぜこの値か |

**避けるべきセクション（実装詳細、陳腐化しやすい）**:

| セクション名 | 理由 |
|-------------|------|
| Called by | 呼び出し元が変更されると陳腐化。IDEの "Find Usages" で検索可能 |
| Delegates to | 委譲先はコードを読めば明らか |
| Dependencies | 具体的なクラス名はコンストラクタを見れば明らか |
| Factory | ファクトリーメソッド名はクラス定義を見れば明らか |
| Fields | Attributes セクションで十分、重複 |
| Contains | Attributes セクションで十分、重複 |
| Type Constraints | 型アノテーションとArgsで十分 |

### 1ファイル1クラスの場合のテンプレート

プロジェクトでは1ファイル1クラス構成が多い。この場合、モジュールdocstringとクラスdocstringで**同じ内容を繰り返してはならない**。

#### モジュールdocstring

```python
"""<層名>の<責務>

<層としての依存方向と設計判断>。
<前提条件や制約>。
"""
```

**例**:

```python
"""Transform層の入力担当

基盤層への薄いラッパー。例外処理やデータ変換は行わず、委譲のみを担当する。
"""
```

#### クラスdocstring

```python
class SomeClass:
    """<具体的な機能を1行で>

    <設計意図を記述: なぜこうするか、制約、ライフサイクルなど>

    <必要に応じてFlow、Lifecycle、Constraints、Scopeなど（セクション名は英語）>
    <実装詳細（Called by、Delegates toなど）は避ける>
    """
```

**例**:

```python
class TextReader:
    """テキストファイルを読み込んで文字列として返す

    基盤層への薄いラッパー。例外処理は行わず、そのまま伝播させる。
    """
```

### メソッドdocstring

型アノテーションが明確で、Args/Returns/Raisesで十分に説明できる場合は、最小限の記述で構わない。

**Returnsセクションの判断基準**:

- **型の言い換えだけなら省略**: 型アノテーションで自明な場合
- **契約を書くなら記述**: 戻り値の意味や制約がある場合

#### 例A: Returnsを省略してよい（型の言い換えのみ）

```python
def provide(self) -> TransformOrchestrator:
    """TransformOrchestrator を生成して返す"""
```

#### 例B: Returnsを書くべき（契約がある）

```python
def read(self, path: Path) -> str:
    r"""テキストファイルを読み込んで文字列を返す

    Args:
        path: 読み込むテキストファイル

    Returns:
        UTF-8でデコードされたファイル内容。BOMは除去される。
    """
```

#### 例C: 複雑なロジック（Flowで処理フローを記述）

処理フローや副作用、注意点があれば詳細に記述する。

```python
def orchestrate(self, context: TransformContext) -> TransformResult:
    """テキストファイルに行番号を付与して出力

    Flow:
        1. TextReaderでファイル読み込み
        2. 各行に行番号を付与
        3. 先頭に現在日時を追加
        4. TextWriterで書き込み

    Args:
        context: Transform処理の実行時コンテキスト

    Returns:
        transform_count は入力テキストの行数を表す
    """
```

## 良い例・悪い例

### ❌ 悪い例: 重複するdocstring

#### 例1: `orchestrator.py`（修正前）

モジュールとクラスが全く同じ内容を繰り返している。

```python
"""テキスト変換オーケストレーター

テキストファイルを読み込み、行番号を付与して出力します。
"""

class TransformOrchestrator:
    """Transformオーケストレーター

    テキストファイルを読み込み、行番号を付与して出力します。
    """
```

**問題点**:
- モジュールとクラスが同じことを繰り返し、情報量が増えていない
- アーキテクチャ上の位置づけや呼び出し元が不明
- 処理フローや戻り値の情報がない

#### 例2: `handler.py`（修正前）

```python
"""エラーハンドラーモジュール

様々な例外タイプを受け取り、適切な形式でエラーメッセージを出力します。
sys.exit は実行せず、ログ出力のみを担当します。
"""

class ErrorHandler:
    """エラーハンドラークラス

    様々な例外タイプを受け取り、適切な形式でエラーメッセージを出力します。
    sys.exit は実行せず、ログ出力のみを担当します。
    """
```

**問題点**:
- モジュールとクラスがほぼ同一
- 呼び出し元や具体的な区別ロジックが不明

### ✅ 良い例: 設計意図を記述したdocstring

#### 例1: `orchestrator.py`（修正後）

```python
"""Transform層の中核

変換パイプライン全体を制御し、入力・変換・出力の流れを調整する。
"""

class TransformOrchestrator:
    """テキストファイルを読み込み、行番号を付与して出力する

    Flow:
        1. TextReaderでファイル読み込み
        2. 各行に行番号を付与
        3. 先頭に現在日時を追加
        4. TextWriterで書き込み

    Returns:
        transform_count は入力テキストの行数を表す
    """
```

**改善点**:
- モジュール: 設計上の役割（パイプライン制御）を簡潔に記述
- クラス: 処理フローの意図を明示（なぜこの順序か）
- 実装詳細（呼び出し元、委譲先）は削除

#### 例2: `handler.py`（修正後）

```python
"""基盤層のエラーログ出力

例外の種類に応じてログフォーマットを切り替える。
sys.exitは実行せず、ログ出力のみを担当する。
"""

class ErrorHandler:
    """例外をログ出力用メッセージにフォーマットして記録する

    例外の型（ApplicationError or 汎用Exception）に応じてフォーマットを切り替える。

    Constraints:
        - sys.exitは呼ばない（終了判断は呼び出し元が行う）
        - ログ出力のみを担当（例外の再送出や変換は行わない）
    """
```

**改善点**:
- モジュール: 設計上の責務（ログ出力のみ）を明示
- クラス: 制約を明示（してはいけないこと）
- 実装詳細（呼び出し元、具体的なフィールド名）は削除

#### 例3: `reader.py`（修正後）

```python
"""Transform層の入力を担当する薄いラッパー

基盤層への委譲のみを行い、例外処理やデータ変換は行わない。
"""

class TextReader:
    """テキストファイルを読み込んで文字列として返す

    基盤層への薄いラッパー。例外処理は行わず、そのまま伝播させる。
    """
```

**改善点**:
- モジュール: 設計上の役割（薄いラッパー）を明示
- クラス: 制約（例外処理しない）を明示
- 実装詳細（Called by、Delegates to）は削除

#### 例4: `fs/protocol.py`（既存の良い例）

```python
"""ファイルシステム操作のプロトコル定義

型安全な依存性注入とテスト容易性を提供するため、
ファイルシステム操作の抽象インターフェースを定義します。
"""

class TextFileSystemReaderProtocol(Protocol):
    """ファイルシステム読み取り専用プロトコル

    ファイル内容の読み込み機能のみを提供します。
    """
```

**良い点**:
- モジュール: プロトコル定義の目的（DI、テスト容易性）を明示
- クラス: 具体的な責務（読み取り専用）を明示
- 重複なく、それぞれ異なる視点で情報を提供

## インラインコメント

### 書くべき場合

以下のような場合にインラインコメントを記述する。

1. **複数行に渡るまとまり（ブロック）の意図を示す**

```python
# ファイル読み込みと行番号付与
text = self.reader.read(context.target_file)
lines = text.splitlines()
numbered_lines = [f"{i + 1}: {line}" for i, line in enumerate(lines)]

# 現在日時を先頭に追加
output_lines = [str(context.current_datetime), *numbered_lines]
```

ブロック単位でコメントすることで、処理の流れを理解しやすくする。**1行ごとの説明は原則しない**（保守コストが高く、コード変更でズレやすい）。

2. **非自明な設計判断や制約**

```python
# sys.exitは呼び出し元が判断するため、ここでは実行しない
logger.log(self.log_level, msg, exc_info=True)
```

3. **将来の拡張ポイントやTODO**

```python
# TODO: 複数ファイル結合に対応する場合はここを拡張
return self.fs_reader.read(path)
```

4. **外部仕様に対応するステップ番号（例外的に使用）**

外部仕様書に「ステップ1、ステップ2」と記載されている場合のみ、対応を明示するためにステップ番号を使う。

```python
# Step 1: 仕様書セクション3.2.1に対応
text = self.reader.read(context.target_file)

# Step 2: 仕様書セクション3.2.2に対応
lines = text.splitlines()
```

### 書かないべき場合

1. **コードが自明な場合**

❌ 悪い例:

```python
# 変数に値を代入
result = transform_count
```

✅ 良い例:

```python
result = transform_count  # コメント不要
```

2. **docstringで既に説明されている内容**

docstringに記載済みの情報を繰り返さない。

3. **変数名やメソッド名で意図が明確な場合**

```python
# ❌ 悪い例
# ユーザーIDを取得
user_id = get_user_id()

# ✅ 良い例
user_id = get_user_id()  # コメント不要（メソッド名で自明）
```

## 既存ルールとの関係

### Google形式（MODEL-003）

プロジェクトの設計原則では、Google形式でdocstringを記述することを定めている。

本ドキュメントはその方針を踏襲し、具体的な書き分け方を補完する。

- モジュールdocstring: 簡潔な概要と設計上の位置づけ
- クラスdocstring: 機能、処理フロー、契約
- メソッドdocstring: Args, Returns, Raises（Google形式）

### Protocol契約（DI-001-1）

プロジェクトの設計原則では、Protocolを使った契約ベース設計を推奨している。

Protocolのdocstringでは、以下を明確にする。

- モジュールdocstring: Protocolの目的（DI、テスト容易性）
- クラスdocstring: 提供する機能の範囲（読み取り専用、書き込み専用など）
- メソッドdocstring: 契約（引数、戻り値、例外）

**例**: `fs/protocol.py`

```python
"""ファイルシステム操作のプロトコル定義

型安全な依存性注入とテスト容易性を提供するため、
ファイルシステム操作の抽象インターフェースを定義します。
"""

class TextFileSystemReaderProtocol(Protocol):
    """ファイルシステム読み取り専用プロトコル

    ファイル内容の読み込み機能のみを提供します。
    """

    def read(self, file_path: Path) -> str:
        """テキストファイルを文字列で読み込む

        Args:
            file_path: 読み込み対象のファイルパス

        Returns:
            ファイルの内容

        Raises:
            FileSystemError: ファイルシステムエラー時
        """
        ...
```

## `__init__.py` のコメント

`__init__.py` は「入口の契約」を書く場所である。公開APIの列挙は `__all__` に任せ、docstringでは列挙しない。

### 方針

**プロダクション `__init__.py`**:

```python
"""<パッケージの役割(層)>。

公開APIは `<package>` から import すること(`__all__` のみ互換性対象)。

Docs:
    - docs/spec/<package>/requirements.md
    - docs/spec/<package>/design.md
"""
```

- パッケージの役割と層を1行で記述
- 公開APIの境界を明示(「`__all__` のみ互換性対象」)
- 公開APIの列挙は `__all__` に任せ、docstringでは列挙しない
- **Docsセクションは常に記述**（仕様書は必ず作成する運用前提）
- パスはリポジトリルート基準で記載（相対パスは避ける）

**テスト `__init__.py`**:

- 空ファイルで配置する（コメントなし、docstringなし）
- 詳細は [packaging.md](packaging.md) を参照

### 良い例

**公開API境界を定義するパッケージ**:

```python
"""エラー処理の公開API(Foundation層)。

公開APIは `example.foundation.error` から import すること(`__all__` のみ互換性対象)。

Docs:
    - docs/spec/error/requirements.md
    - docs/spec/error/design.md
"""

from example.foundation.error.error import ApplicationError
from example.foundation.error.handler import ErrorHandler

__all__ = [
    "ApplicationError",
    "ErrorHandler",
]
```

**ルートパッケージ**:

```python
"""Exampleアプリケーションのルートパッケージ。"""

__all__: list[str] = []
```

**中間パッケージ(re-exportなし)**:

```python
"""基盤層の共通コンポーネント(Foundation層)。"""
```


### 悪い例

**❌ 公開APIを列挙している**:

```python
"""設定管理パッケージ

## 公開API

- PathConfig: パス設定クラス
"""
```

理由: `__all__` を見れば十分。docstringで列挙すると二重管理になる。

**❌ 相対パスでドキュメントリンクを書いている**:

```python
"""テキスト変換システム

詳細は以下を参照:
- [要件定義](../../../docs/spec/transform/requirements.md)
"""
```

理由: 相対パスはファイル移動で壊れる。仕様書が存在する場合のみ、リポジトリルート基準で記載。

**❌ テスト `__init__.py` にコメントや docstring を書いている**:

理由: テストの `__init__.py` は空ファイルとする。
コメントや docstring を書くと、プロダクションパッケージと同じ管理コストが発生する。
詳細は [packaging.md](packaging.md) を参照。

## テストコードのコメント

テストコードには、プロダクションコードとは異なるコメント方針を適用する。

### テストメソッドのdocstring

**原則: テストメソッドにdocstringは書かない**

理由:
- テスト失敗時に読むのはテスト名とassert周りであり、docstringはほぼ読まれない
- テスト名とdocstringの二重記述は保守コストが高い
- テスト名に情報を集約することで、一箇所の更新で済む

**例外: テスト名に書けない背景情報がある場合のみ**

テスト名だけでは理解できない特殊な前提条件や、外部仕様への参照がある場合のみ、最小限のdocstringを記述する。

```python
# ❌ 悪い例: テスト名と同じ内容を繰り返す
def test_read_正常系_ファイル内容を文字列で返す(self, tmp_path: Path):
    """実際のファイルを作成して読み込みテスト"""
    # ...

# ✅ 良い例: docstringなし（テスト名で十分）
def test_read_正常系_ファイル内容を文字列で返す(self, tmp_path: Path):
    # Arrange
    # ...
```

### Arrange/Act/Assertコメント

**原則: 常に書く（ただし内容があるセクションのみ）**

すべてのテストメソッドに `# Arrange`, `# Act`, `# Assert` コメントを記述する。
ただし、Arrange に記述するコードがない場合は `# Arrange` コメントを省略する。

理由:
- 「このテストにはArrange/Act/Assertコメントが必要か」という判断コストを排除
- 一貫性を保つことで、コードレビューや保守が容易になる
- テストの構造が明確になり、可読性が向上
- 内容のない `# Arrange` は視覚的ノイズになるため省略する

```python
# ✅ 良い例: Arrange に内容があれば記述
def test_provide_正常系_TransformOrchestratorインスタンスを返す(self):
    # Arrange
    provider = TransformOrchestratorProvider()

    # Act
    result = provider.provide()

    # Assert
    assert isinstance(result, TransformOrchestrator)


# ✅ 良い例: Arrange に内容がなければ省略
def test_from_base_dir_正常系_tmpディレクトリを生成(self, tmp_path: Path):
    # Act
    result = PathConfig.from_base_dir(tmp_path)

    # Assert
    assert result.tmp_dir == tmp_path / "tmp"
```

**例外: Act & Assert が同時の場合**

例外送出のテストなど、ActとAssertが同時に行われる場合は `# Act & Assert` と記述する。

```python
def test_read_異常系_存在しないファイルでFileSystemError(self):
    # Arrange
    reader = TextFileSystemReader()

    # Act & Assert
    with pytest.raises(FileSystemError):
        reader.read(Path("存在しないファイル.txt"))
```

### テストクラスのdocstring

**原則: 1行docstringを記述**

テストクラスには、テスト対象クラスを示す1行docstringを記述する。

```python
class TestTextReader:
    """TextReaderクラスのテスト"""
```

**目的**: テスト対象の明示を統一し、クラス名の検索性を高める。

**例外的に補足が必要な場合**

テスト名やコードから読み取りづらい情報がある場合のみ、最小限の補足を追加する。セクション形式（Args, Returns など）は使わない。

```python
class TestErrorHandler:
    """ErrorHandler クラスのテスト

    エラーハンドラーのログ出力処理をテストします。
    sys.exit は含まれず、エラーメッセージのログ出力のみを担当します。
    """
```

## コメント更新責任

**原則: 古いコメントは最悪、削除を推奨**

コメントがコードより古い状態は、誤解を招き保守を妨げる。以下の原則に従う:

1. **コード変更時にコメントも更新する**
   - コメントが正しくない場合は即座に修正
   - 修正が困難なら削除する（古い情報より無い方が良い）

2. **外部仕様への参照を優先**
   - docstringで仕様を写経しない
   - 仕様書へのパス（Docsセクション）を記載し、設計判断と契約に集中

3. **陳腐化しやすい情報は書かない**
   - 具体的なクラス名、呼び出し元、委譲先（避けるべきセクション参照）
   - これらはIDEの検索機能で確認可能

**例**:

```python
# ❌ 悪い例: 仕様の写経（仕様変更で陳腐化）
def validate(self, data: dict) -> bool:
    """データを検証する

    検証ルール:
    - name は必須、50文字以内
    - email は必須、有効な形式
    - age は任意、0以上
    """

# ✅ 良い例: 仕様への参照と設計判断
def validate(self, data: dict) -> bool:
    """検証ルールに基づいてデータを検証する

    検証ルール詳細は docs/spec/validation/requirements.md を参照。

    Constraints:
        - 検証エラー時は False を返す（例外は送出しない）
        - ログ出力は行わない（呼び出し元が責務を持つ）
    """
```

## まとめ

- **モジュールdocstring**: 設計上の位置づけ、層としての依存方向、制約
- **クラスdocstring**: 具体的な機能、処理フロー、契約
- **メソッドdocstring**: 型の言い換えだけなら省略、契約があれば記述
- **インラインコメント**: ブロック単位で記述、1行ごとの説明は避ける
- **重複排除**: モジュールとクラスで同じ内容を繰り返さない
- **`__init__.py`**: プロダクションでは必須（Docsセクションを常に記述）、テストでは空ファイルで配置
- **テストメソッドdocstring**: 書かない（テスト名に集約）
- **Arrange/Act/Assertコメント**: 常に書く（一貫性と判断コスト排除）
- **テストクラスdocstring**: 1行で最小限に
- **コメント更新責任**: 古いコメントは削除を推奨、仕様への参照を優先

## ツール設定

本ドキュメントの方針に対応する `pyproject.toml` の設定内容（ruff の `select`、`ignore`、`per-file-ignores`、`convention` など）は別ドキュメントに集約している。
