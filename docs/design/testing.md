# Pythonテスト設計

本プロジェクトのPythonテストコードにおける設計原則・構造・パターンを示す。

## テストの種類と配置

本プロジェクトはユニットテストとインテグレーションテストの2種類を使い分ける。

| 種類 | 配置先 | 実行コマンド | スコープ | 外部依存 |
|------|--------|------------|--------|--------|
| ユニットテスト | `tests/unit/` | `make test-unit` | 単一クラス・関数の振る舞い | Fake で完全に分離する |
| インテグレーションテスト | `tests/integration/` | `make test-integration` | CLI から結果出力までのエンドツーエンド | 外部ネットワークのみ分離する |

`tests/unit/` の内部構造はプロダクションコードのパッケージ構成をミラーリングする。
対応するプロダクションパッケージに `test_` プレフィックスを付けたディレクトリ名を使う。

```
src/example/transform/         →  tests/unit/test_transform/
src/example/config/            →  tests/unit/test_config/
src/example/foundation/fs/     →  tests/unit/test_foundation/test_fs/
```

## テスト設計の原則

### Fake によるテスト分離

ユニットテストでは Mock を原則として使わない。
代わりに Protocol に適合する、具象クラス（Fake）で外部依存を分離する。

### Protocol との連携

Fake は Protocol の Structural Subtyping を利用する。
Protocol に明示的に継承しなくても、メソッドシグネチャが一致していれば準拠できる。
これにより、Fake をプロダクションコードに依存させずに独立して管理できる。

### AAA（Arrange-Act-Assert）パターン

すべてのテストメソッドは AAA パターンで構造化する。

```python
def test_xxx(self):
    # Arrange
    ...

    # Act
    result = ...

    # Assert
    assert ...
```

### テストの独立性

各テストメソッドは他のテストメソッドに依存しない。
テストの実行順序が変わっても結果が変わらないようにする。
共有状態（クラス変数・グローバル変数）を使わない。

## Fake パターン

### 設計思想

Fake は Protocol に適合する具象クラスである。
Protocol の定義に従ってメソッドシグネチャを実装し、テスト目的に特化した振る舞いを持たせる。
呼び出し時の引数を公開フィールドに保持することで、テストから呼び出し内容をアサートできる。

### Fake の配置ルール

| 配置先 | 対象 |
|--------|------|
| `tests/unit/fake/` | 複数のパッケージのテストで共有する Fake |
| `tests/unit/test_<package>/fake.py` | 特定パッケージのテストのみで使う Fake |

`tests/unit/fake/` に配置した Fake は `__init__.py` で公開し、テストコードから `from tests.unit.fake import ...` でインポートする。

### Fake の実装パターン

コンストラクタで戻り値を事前設定し、呼び出し時の引数を公開フィールドに保持する。

```python
class InMemoryFsReader:
    """TextFileSystemReaderProtocol の InMemory 実装"""

    def __init__(self, text: str = ""):
        self.text = text
        self.file_path: Path | None = None

    def read(self, file_path: Path) -> str:
        self.file_path = file_path  # 呼び出し追跡
        return self.text


class InMemoryFsWriter:
    """TextFileSystemWriterProtocol の InMemory 実装"""

    def __init__(self):
        self.text: str | None = None
        self.file_path: Path | None = None

    def write(self, text: str, file_path: Path) -> None:
        self.text = text
        self.file_path = file_path
```

## テストの命名規則

### テストクラス名

テスト対象クラス名に `Test` プレフィックスを付ける。

```
TransformOrchestrator          →  TestTransformOrchestrator
TransformOrchestratorProvider  →  TestTransformOrchestratorProvider
InMemoryFsReader               →  TestInMemoryFsReader
```

### テストメソッド名

`test_<対象メソッド>_<系統>_<期待する振る舞い>` の形式で日本語を用いて命名する。

| 要素 | 内容 | 例 |
|------|------|-----|
| `<対象メソッド>` | テスト対象のメソッド名（英語） | `orchestrate`、`provide`、`read` |
| `<系統>` | 正常系 / 異常系 / エッジケース | `正常系`、`異常系`、`エッジケース` |
| `<期待する振る舞い>` | テストが確認する内容（日本語） | `TransformOrchestratorインスタンスを返す`、`FileSystemErrorが発生すること` |

```python
def test_orchestrate_正常系_target_fileを読み込んで変換結果を書き込むこと(self): ...
def test_provide_正常系_TransformOrchestratorインスタンスを返す(self): ...
def test_read_異常系_存在しないファイルでFileSystemError(self): ...
```

## テストの構造

### AAA パターンのコメント規約

`# Arrange`、`# Act`、`# Assert` のコメントを必ず付ける。
`pytest.raises` を使う場合は `# Act & Assert` とまとめて記述する。
補足が必要な場合はコメントを追記する。

```python
def test_orchestrate_正常系_target_fileを読み込んで変換結果を書き込むこと(self):
    # Arrange
    fs_reader = InMemoryFsReader(text="line1\nline2\nline3")
    fs_writer = InMemoryFsWriter()
    orchestrator = TransformOrchestrator(
        reader=TextReader(fs_reader),
        transformer=TextTransformer(),
        writer=TextWriter(fs_writer),
    )
    context = TransformContext(
        target_file=Path("input.txt"),
        tmp_dir=Path("/tmp/output"),
        current_datetime=datetime(2024, 12, 26, 15, 30, 45),
    )

    # Act
    result = orchestrator.orchestrate(context)

    # Assert
    assert result.src_length == 3
```

```python
def test_read_異常系_存在しないファイルでFileSystemError(self):
    # Arrange
    reader = TextFileSystemReader()

    # Act & Assert
    with pytest.raises(FileSystemError):
        reader.read(Path("存在しないファイル.txt"))
```

### フィクスチャの使い方

pytest の組み込みフィクスチャを用途に応じて使い分ける。

| フィクスチャ | 用途 |
|------------|------|
| `tmp_path: Path` | ファイルシステムを使うテストで一時ディレクトリを確保する |
| `caplog: pytest.LogCaptureFixture` | ログ出力の内容を検証する |
| `monkeypatch: pytest.MonkeyPatch` | 環境変数の設定・削除、属性のパッチ当て |

インテグレーションテストでは `tmp_path` をベースに専用フィクスチャを定義する。

```python
@pytest.fixture
def tmp_dir(tmp_path: Path) -> Path:
    """インテグレーションテスト用ワークスペース"""
    test_dir = tmp_path / "integration_test"
    test_dir.mkdir()
    return test_dir
```

## ユニットテスト

### プロダクションコードとの1対1マッピング

テストファイルはプロダクションコードのファイルと1対1で対応させる。

```
src/example/transform/orchestrator.py  →  tests/unit/test_transform/test_orchestrator.py
src/example/transform/reader.py        →  tests/unit/test_transform/test_reader.py
src/example/transform/transformer.py  →  tests/unit/test_transform/test_transformer.py
```

### Orchestrator テスト

Orchestrator のテストでは、コンストラクタに Fake を注入して振る舞いを検証する。

```python
class TestTransformOrchestrator:
    def test_orchestrate_正常系_target_fileを読み込んで変換結果を書き込むこと(self):
        # Arrange
        fs_reader = InMemoryFsReader(text="line1\nline2\nline3")
        fs_writer = InMemoryFsWriter()
        orchestrator = TransformOrchestrator(
            reader=TextReader(fs_reader),
            transformer=TextTransformer(),
            writer=TextWriter(fs_writer),
        )
        context = TransformContext(
            target_file=Path("input.txt"),
            tmp_dir=Path("/tmp/output"),
            current_datetime=datetime(2024, 12, 26, 15, 30, 45),
        )

        # Act
        result = orchestrator.orchestrate(context)

        # Assert
        assert result.src_length == 3
```

### Provider テスト（Composition Root の検証）

Provider テストは、`provide()` が返すオブジェクトの型を検証する。

```python
class TestTransformOrchestratorProvider:
    def test_provide_正常系_TransformOrchestratorインスタンスを返す(self):
        # Act
        result = TransformOrchestratorProvider().provide()

        # Assert
        assert isinstance(result, TransformOrchestrator)
```

Provider テストでは Fake を使わず、実際の依存関係グラフが正しく構築されることを検証する。

## インテグレーションテスト

### subprocess 方式

インテグレーションテストは `subprocess.run` で CLI を子プロセスとして起動し、標準出力・標準エラー出力・終了コードを検証する。

```python
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
    data = json.loads(result.stdout)
    assert "src_length" in data
```

subprocess 方式を採用する理由は次のとおりである。

- CLI の引数解析・環境変数読み込み・終了コードまで含めたエンドツーエンド検証ができる
- プロセス境界を越えることで、実際の動作環境に近い検証ができる
- `pyproject.toml` の `patch = ["subprocess"]` 設定により、子プロセスのカバレッジも計測できる

### 環境変数の注入パターン

`subprocess.run` の `env=` 引数で環境変数をマージして渡す。
CLIオプションと環境変数の優先度を検証するときに使う。

```python
result = subprocess.run(
    cmd,
    cwd=tmp_dir,
    capture_output=True,
    text=True,
    timeout=10,
    env={**os.environ, "EXAMPLE_TMP_DIR": str(env_tmp_dir)},
)
```

### テストケースの選定基準

インテグレーションテストはハッピーパス（正常系の代表ケース）を中心に選ぶ。
境界値・エラー系・詳細な条件分岐はユニットテストで網羅する。

### ユニットテストとの棲み分け

| 観点 | ユニットテスト | インテグレーションテスト |
|------|------------|---------.|
| テスト数 | 多い（境界値・エラー系・詳細ケース） | 少ない（ハッピーパス中心） |
| 実行速度 | 高速 | 低速（プロセス起動コストあり） |
| 追加基準 | 新しいクラス・メソッドを追加したとき | ユニットテストで代替できないエンドツーエンドの検証が必要なとき |

## conftest.py の役割

`tests/conftest.py`（ルートレベル）は `pytest_configure` フックでグローバルな環境変数を設定する。
テスト収集・実行前にモジュールがインポートされる前の段階で実行される。

```python
def pytest_configure() -> None:
    """pytest設定フック: テスト実行前に環境変数を設定"""
    os.environ["EXAMPLE_LOG_LEVEL"] = "WARNING"
```

各テストパッケージ配下には `conftest.py` を置かない。
フィクスチャが必要な場合はテストファイル内に定義する。

## ガードレール

### 禁止事項

| ルール | 理由 |
|-------|------|
| `unittest.mock` / `pytest-mock` の `MagicMock` / `patch` を使わない | Protocol + Fake で型安全に分離できる。Mock は型チェックを回避する |
| `@pytest.mark.parametrize` を使わない | 各テストメソッドが独立した意図を持ち、命名で識別できることを優先する |
| テストクラスをネストしない | フラットな構造で十分。ネストは可読性を下げる |
| テスト間で状態を共有しない（クラス変数・グローバル変数） | テストの実行順依存を防ぐ |
| `conftest.py` にビジネスロジックを持ち込まない | `conftest.py` はフィクスチャの定義と `pytest_configure` のみ |
