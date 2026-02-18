# pyproject.toml 設計ガイドライン

## 目的

このドキュメントは `pyproject.toml` の設定における「設計意図の記録」として機能する。

各ツールの設定項目は公式ドキュメントを読まなければ意図が分からない。特に Ruff の `ignore/unfixable/per-file-ignores` や Pyright の診断レベル設定は「なぜその値なのか」がコードから読み取れない。本ドキュメントはその「なぜ」を補足する。

対象セクションは `[project]` を除く、ビルドシステム・テスト・Linter・型チェックの各設定とする。既存の [comment.md](comment.md) と [packaging.md](packaging.md) の「推奨ツール設定」セクションで一部の設定を解説しているため、本ドキュメントはそれらを補完・参照する位置づけとする。

## CLIエントリーポイント（project.scripts）

`project.scripts` はコマンド名とエントリーポイント関数のマッピングを定義する。

記法は `コマンド名 = "モジュールパス:関数名"` という形式を取る。`example.cli:main` は「`example.cli` モジュール内の `main` 関数をエントリーポイントとして登録する」という意味である。パッケージのインストール後、`example` コマンドを実行すると `example.cli.main()` が呼ばれる仕組みである。

`uv run example` のように実行できるのは、この設定によって実行可能スクリプトが生成されるためである。

## ビルドシステム（build-system / tool.hatch）

### hatchling を選んだ理由

`hatchling` は Hatch プロジェクトが提供するビルドバックエンドである。`setuptools` と比較して以下の点で優れている。

- 設定が `pyproject.toml` に完結する（`setup.py` や `setup.cfg` が不要）
- デフォルト動作が現代的なプロジェクト構成（`src` レイアウト）を前提としている
- 設定の学習コストが低く、最小限の記述で機能する

### packages の明示指定

`src` レイアウトを採用する場合、`packages = ["src/example"]` を明示的に指定している。

自動検出に任せると `src/` 配下の意図しないディレクトリ（`src/tool/` 等）を拾う可能性がある。明示することでビルド成果物に含まれるパッケージを確実に制御できる。

## 開発依存（dependency-groups）

`[dependency-groups]` は PEP 735 で標準化されたグループ定義である。`[project.optional-dependencies]` との違いは、インストール成果物（wheel/sdist）に含まれない点にある。開発・CI 専用のツールに使うのが意図された用途である。

`dev` グループに含まれるツールの役割を 3 軸で分類する。

| ツール | 役割 | 分類 |
|--------|------|------|
| pytest | テスト実行フレームワーク | テスト |
| pytest-mock | モックオブジェクト生成 | テスト |
| pytest-asyncio | 非同期テスト対応 | テスト |
| pytest-cov | カバレッジ計測 | テスト |
| vulture | 未使用コード検出 | 品質 |
| ruff | Linter・フォーマッタ | 品質 |
| pyright | 静的型チェッカー | 型 |

## テスト設定（tool.pytest / tool.coverage）

### pytest

`asyncio_mode = "strict"` と `asyncio_default_fixture_loop_scope = "function"` はセットで機能する設定である。

`strict` モードでは、非同期テストを `@pytest.mark.asyncio` デコレータで明示的に指定することを強制する。無指定の非同期関数を誤ってテストとして扱うことを防ぐ意図がある。

`asyncio_default_fixture_loop_scope = "function"` は、各テスト関数が独立したイベントループを使用することを保証する。テスト間の状態汚染を防ぎ、テストの独立性を高める。

`pythonpath` と `testpaths` の方針については [packaging.md](packaging.md) の「推奨ツール設定 / pytest」セクションを参照。

### coverage

`patch = ["subprocess"]` は、サブプロセスとして起動された Python プロセスでもカバレッジを計測するための設定である。

通常、カバレッジ計測はメインプロセス内でのみ機能する。`subprocess.Popen` や `subprocess.run` で子プロセスを起動した場合、その中で実行されるコードはカバレッジに含まれない。`patch = ["subprocess"]` を指定すると pytest-cov が `subprocess` モジュールをパッチし、子プロセス起動時にカバレッジ引き継ぎの仕組みを自動で注入する。

`source = ["src"]` はカバレッジ計測の対象を `src/` 配下に限定する設定で、テストコードやツール類がレポートに混入することを防ぐ。

## Linter設定（tool.ruff）

### 基本設定

`line-length = 100` は Python 標準の 79 文字より長い値を設定している。URL や日本語を含む行が 79 文字制限に引っかかりやすいため、現実的な長さとして 100 文字を採用した。実際の行長オーバーは `E501` を無効化しているため lint エラーにはならず、フォーマッタとコードレビューで対処する運用となっている。

`target-version = "py313"` は Python 3.13 向けの構文・ルールを適用する設定である。`requires-python` と合わせることで、古い Python の互換性を気にした余計な提案が出ないようにする。

`exclude` は Ruff の検査対象から除外するディレクトリを指定する。`.git`・`.ruff_cache`・`.venv` はツールのメタデータや仮想環境のため除外する。`.vscode` は IDE 設定ファイルであり Lint 対象外とする。`tool` は補助スクリプト類を配置するディレクトリで、本番コードとは別扱いとする。

### 有効化ルールの選定方針

有効化するルールを役割別に分類する。

| グループ | プレフィックス | 役割 |
|----------|---------------|------|
| バグ直結 | F, B | 未定義参照、未使用コード、バグの温床となるパターンを検出 |
| コードスタイル | E, W, I | 基本的なスタイル統一、import 順序整列 |
| モダン化 | UP, SIM, PTH | 現代的な Python 構文への移行促進、冗長な表現の簡素化 |
| ドキュメント | D | docstring の存在・形式チェック |
| Ruff 独自 | RUF | 実用的な補助検出（曖昧 Unicode など） |

### 無効化ルールの分類と理由

無効化ルールを 4 カテゴリに分類して意図を明示する。

**日本語対応** — RUF001, RUF002, RUF003, D400, D415

日本語文字列・コメント・docstring を許容するための無効化。英語前提のルールは日本語コードベースで大量に誤検知する。

**LLM 生成コード配慮** — B007, B008, B905, B019

生成コードで頻出し、開発を阻害するため全体では無効化する。厳格化が必要な場合は `per-file-ignores` で対応する。

- B007（未使用ループ変数）: クロージャ束縛や一時変数として LLM が生成しやすい
- B008（デフォルト引数内での関数呼び出し）: 生成コードに現れやすいが意図的な場合もある
- B905（`zip(strict=True)` の強制）: 本番コードのみ厳格化したい場合は `per-file-ignores` で個別に有効化する
- B019（メソッドへの `lru_cache`）: `DictionaryLoader` 等で意図的に使用するケースがある

**ルール競合（Google 方式）** — D203, D213

`D203/D211` と `D212/D213` はそれぞれ競合するペアである。両方を有効にすると ruff がエラーを返す構造になっており、Google 方式で採用した側（D211, D212）を活かし、競合する側（D203, D213）を無効化する。詳細は [comment.md](comment.md) の「推奨ツール設定 / docstringのスタイル（Google方式）」セクションを参照。

**可読性・移行コスト** — SIM105, SIM108, SIM116, UP042

提案の意図は理解できるが可読性への影響が大きく、コードベース全体の一貫性を壊す可能性があるため無効化する。

- SIM105（`try-except-pass` → `contextlib.suppress`）、SIM108（`else` 省略提案）、SIM116（`if` → `dict` マップ置換）: いずれも簡素化の提案だが画一的に適用すると読みにくくなる
- UP042（`StrEnum` への移行）: 既存コードが動作している間は移行コストを発生させたくないため当面維持する

### 自動修正の対象外（unfixable）

`unfixable` は「検出はする・自動修正はしない」という二段構えの設計を実現する設定である。

自動修正を有効にすると、ruff が意図しないコードを削除してしまう危険がある。以下の 2 ルールを対象外とする。

- **F401（未使用 import）**: `__init__.py` での re-export は構文上「未使用」に見えるが、公開 API として意図的に必要。自動削除されると公開 API が壊れる。re-export の方針については [packaging.md](packaging.md) の「re-export」セクションを参照。
- **F841（未使用変数）**: デバッグ用フックや将来拡張のプレースホルダとして一時的に置く場合がある。削除すると開発の流れを妨げる。

### パス別の緩和（per-file-ignores）

本番コードは厳しめ、周辺コードは緩めの運用を `per-file-ignores` で実現する。

| パターン | 緩和するルール | 理由 |
|---------|--------------|------|
| `**/__init__.py` | F401 | re-export の未使用 import を許容（詳細は [packaging.md](packaging.md) 参照） |
| `tests/**` | B905, D100, D101, D102, D107 | テストでは `zip(strict=True)` を強制せず、docstring も不要（詳細は [comment.md](comment.md) 参照） |

### docstringスタイル（pydocstyle）

`convention = "google"` を指定すると、pydocstyle の Google スタイル準拠ルールセットが自動的に有効・無効になる。具体的には D212（要約行は 1 行目）が有効になり、その代わりに競合する D213 は自動的に無効扱いとなる。

`convention` を指定することで、Google スタイルに合わないルールを個別に無効化する手間が省ける。詳細は [comment.md](comment.md) の「既存ルールとの関係 / Google形式（MODEL-003）」セクションを参照。

## 型チェック設定（tool.pyright）

### 検査対象とスコープ

`include = ["src", "tests"]` で本番コードとテストコードの両方を検査対象とする。`.venv` や `build`、`dist`、`__pycache__`、`tool` は検査から除外する。

`pythonVersion = "3.13"` は型チェックに使用する Python バージョンを指定する。`requires-python` および `[tool.ruff]` の `target-version` と揃えることで、バージョン依存の型推論・ルール適用が一貫する。

`typeCheckingMode = "basic"` を採用した理由は、開発初期の速度優先である。`strict` モードにすると型アノテーションが不完全なコードでエラーが多発し、開発の流れが止まりやすい。`basic` モードで「バグに直結するものだけエラーにする」方針を取りつつ、個別設定で重要な項目を `error` に昇格させる二段構えを採用している。

### 実行環境の分離（executionEnvironments）

`executionEnvironments` は「どのディレクトリのコードがどの import パスを持つか」を pyright に伝える設定である。

- `root = "src"` の環境: `extraPaths = ["src"]` を設定し、`src/` 配下のモジュールを互いに import できるようにする
- `root = "tests"` の環境: `extraPaths = ["src", "."]` を設定し、テストから本番コードとテスト補助モジュールの両方にアクセスできるようにする

`"."` がプロジェクトルートを意味し、`tests/` 直下に配置した補助モジュールを pyright が解決できるようになる。詳細な import 解決の方針は [packaging.md](packaging.md) の「推奨ツール設定 / pyright」セクションを参照。

### 診断レベルの設計思想

pyright の診断レベルは `"error"`, `"warning"`, `"none"` の 3 段階である。

| レベル | 意味 | 使いどころ |
|--------|------|-----------|
| `"error"` | CI を止める。コミット前に修正必須 | バグに直結する問題 |
| `"warning"` | 開発の流れを止めない。後で対処可能 | 重要だが初期に多発する問題 |
| `"none"` | 完全無効化。ノイズが多すぎる場合に使用 | 初期段階では情報量が多すぎるもの |

`typeCheckingMode = "basic"` はデフォルトで多くのチェックを `"warning"` 水準に設定するが、個別設定で重要度に応じて `"error"` または `"none"` に調整する。

### エラー昇格の判断基準

**エラーに昇格するもの（バグに直結する）**:

- `reportIncompatibleMethodOverride`, `reportIncompatibleVariableOverride`: オーバーライドの型不整合は実行時エラーに直結する
- `reportUnusedCoroutine`: `await` 忘れはコルーチンが実行されない実行不具合になる
- `reportMatchNotExhaustive`: `match` 文で網羅漏れがあると想定外のケースで処理が抜ける
- `reportOverlappingOverload`: オーバーロード定義の矛盾は型推論の誤動作を招く
- `reportUnknownVariableType`, `reportUnknownParameterType`, `reportMissingTypeArgument`: 型ヒント必須の方針（MODEL-003-1）を機械的に強制する

**警告に留めるもの（開発をブロックしたくない）**:

- `reportMissingImports`, `reportMissingModuleSource`: 依存ライブラリの導入前に import を書くことがある。エラーにすると新規ライブラリ追加の際に開発が止まる
- `reportCallIssue`, `reportAttributeAccessIssue`: 呼び出し不能・属性不在の検出は重要なため完全無効化せず最低限の安全網として残す
- `reportPrivateUsage`: `_private` な要素の外部使用を抑制するが、開発中は一時的に許容したい場面がある
- `reportUnknownArgumentType`, `reportUnknownLambdaType`: 生成コードに多いため開発をブロックしない
- `reportUnusedImport`, `reportUnusedVariable`: 未使用の import・変数は警告に留め、生成コードでの一時変数を許容する。Ruff との併用で自動修正と両立できる

**無効化するもの（ノイズが多すぎる）**:

- `reportMissingTypeStubs`: サードパーティの型スタブ不足は初期開発では無視してスピードを優先する
- `reportUnknownMemberType`: `list.append` などの基本操作で頻発するため無効化する。重要な属性エラーは `reportAttributeAccessIssue` で別途検出する

`useLibraryCodeForTypes = true` は型スタブが存在しない場合でも実装コードから型推論を行い、IDE 補完の精度を向上させる設定である。`reportMissingTypeStubs` を `"none"` にしつつも、型情報を最大限に活用する意図がある。
