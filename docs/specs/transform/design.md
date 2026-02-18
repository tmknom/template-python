# transform パッケージ基本設計

[transform パッケージ要件定義](./requirements.md) に基づいた基本設計を説明します。

## 1. アーキテクチャパターン

[Pythonアーキテクチャ設計](../../design/architecture.md) に記載のパターンを採用している。

- **Composition Root + Orchestrator パターン**: 依存関係の組み立て（Provider）と処理フロー制御（Orchestrator）の分離
- **オニオンアーキテクチャ**: ファイルシステム操作を Protocol で抽象化し、副作用を分離
- **Context パターン**: コマンド引数・環境設定（パスなど）・ランタイム情報（現在日時）などの実行時パラメータは、Context にカプセル化して Orchestrator へ渡す
- **型設計**: 値オブジェクトでは dataclass や NewType などを使い分け、Types分離で循環依存回避

## 2. コンポーネント構成

### 2.1 主要コンポーネント

| コンポーネント | クラス名 | 役割 |
|---|---|---|
| プロバイダー | `TransformOrchestratorProvider` | 依存関係の組み立て（Composition Root） |
| オーケストレーター | `TransformOrchestrator` | 変換パイプライン全体の制御 |
| テキスト読み込み | `TextReader` | ファイル読み込みを foundation パッケージへの委譲 |
| テキスト変換 | `TextTransformer` | 行番号付与・日時ヘッダー追加の変換ロジック |
| テキスト書き込み | `TextWriter` | ファイル書き込みを foundation パッケージへの委譲 |
| 実行コンテキスト | `TransformContext` | 変換処理の実行時パラメータ（値オブジェクト） |
| 変換結果 | `TransformResult` | 変換処理の結果情報（値オブジェクト） |
| テキスト型 | `SrcText` / `DstText` | 入力・出力テキストを区別する NewType |

### 2.2 ファイルレイアウト

#### プロダクションコード

```bash
src/example/transform/
├── __init__.py       # 公開 APIの定義
├── context.py        # TransformContext
├── orchestrator.py   # TransformOrchestrator
├── provider.py       # TransformOrchestratorProvider
├── reader.py         # TextReader
├── transformer.py    # TextTransformer
├── types.py          # TransformResult, SrcText, DstText
└── writer.py         # TextWriter
```

#### テストコード

```bash
tests/unit/test_transform/
├── fakes.py          # テスト用 Fake（FS Protocol のスタブ実装）
├── test_context.py   # TransformContext のテスト
├── test_orchestrator.py  # TransformOrchestrator のテスト
├── test_provider.py  # TransformOrchestratorProvider のテスト
├── test_reader.py    # TextReader のテスト
├── test_transformer.py   # TextTransformer のテスト
├── test_types.py     # TransformResult のテスト
└── test_writer.py    # TextWriter のテスト
```

## 3. 処理フロー

### 3.1 全体フロー

全体の処理フローは `TransformOrchestrator` が担います。

1. 指定されたファイルを読み込む（`TextReader`）
2. 読み込んだテキストを変換する（`TextTransformer`）
3. 指定したディレクトリへ、変換済みテキストを出力する（`TextWriter`）

### 3.2 変換ロジック

テキストの変換ロジックは `TextTransformer` が担います。

```
入力テキスト（例）:
  hello
  world

変換後テキスト:
  2024-01-01 12:00:00    ← current_datetime をヘッダーとして追加
  1: hello               ← 1始まりで行番号を付与
  2: world
```

## 4. 固有の設計判断

### 4.1 薄いラッパーとしての TextReader / TextWriter

**設計の意図**: `TextReader` と `TextWriter` は foundation パッケージの Protocol への委譲のみを行い、例外処理やデータ変換を行わない。

**なぜそう設計したか**: transform パッケージは変換ロジックに集中すべきであり、I/O エラーの処理方針は呼び出し元（アプリケーションパッケージ）で決定する方が適切である。ラッパー内で例外を握りつぶしたり変換したりすると、エラーハンドリングの方針が分散して保守コストが増大する。また、薄いラッパーに留めることでラッパー自体のテストが不要になり、テスト対象を変換ロジック（`TextTransformer`）に集中できる。

**トレードオフ**: 例外は基盤パッケージから直接呼び出し元まで伝播するため、エラーの意味づけ（ドメイン例外への変換）が必要な場合は別途対処が必要になる。

### 4.2 変換結果に元テキストの行数を使用

**設計の意図**: `TransformResult.length` には変換後のテキスト行数ではなく、入力テキストの行数を格納する。

**なぜそう設計したか**: 変換後テキストには日時ヘッダー行が追加されるため、変換後の行数は入力行数 + 1 となる。呼び出し元が「いくつのテキスト行を変換したか」を知りたい場合、意味的に正しいのは入力テキストの行数である。

### 4.3 SrcText / DstText による入出力テキストの型分離

**設計の意図**: 変換前後のテキストを NewType で `SrcText`（入力）と `DstText`（出力）に区別し、各メソッドのシグネチャに反映する。

**なぜそう設計したか**: 変換前後のテキストはいずれも `str` だが意味的に異なる値である。型で区別することで誤った受け渡しを、静的解析で検出できる。ランタイムでは通常の `str` と同一のため、追加コストはない。

### 4.4 テストコード: Fake による副作用の分離

**設計の意図**: テストでは実際のファイルシステムにアクセスせず、`fakes.py` に定義された Fake（foundation の FS Protocol のスタブ実装）を使用する。

**なぜそう設計したか**: ファイルシステムへのアクセスは副作用であり、テストに含めると実行速度の低下・環境依存・テスト間の干渉が生じる。foundation パッケージが Protocol でファイルシステムを抽象化しているため、テスト時は Fake に差し替えることで、変換ロジック単体を副作用なしに検証できる。

**制約**: 新規テストを追加する場合は `fakes.py` の Fake を使うこと。独自のモックやパッチを使ってファイルシステムをスタブにしてはならない。Fake の実装を変更・拡張する場合も `fakes.py` に集約する。

## 5. 制約と注意点

### 5.1 公開 API の制限

公開 API は `TransformContext` と `TransformOrchestratorProvider` のみ（`__all__` で明示）。内部コンポーネントは外部パッケージからの import を想定しない。

### 5.2 出力パスの決定ルール

出力ファイルパスは `TransformContext.tmp_dir / TransformContext.target_file.name` で決定する。入力ファイルと同じファイル名で、出力先ディレクトリ配下に配置される。

### 5.3 TransformContext の組み立て責務

`TransformContext` の各フィールドは、transform パッケージ外の呼び出し元が組み立てて渡す。フィールドごとに出所が異なり、CLI 引数・設定値・ランタイム情報といった異なるソースをまとめて Orchestrator へ渡すのが Context パターンの役割である。transform パッケージ自体はフィールドの取得方法に関知しない。

## 6. 変更パターン別ガイド

よくある変更ケースと、対応するファイルの道筋を示す。

| 変更内容 | 主な変更対象 | 備考 |
|---|---|---|
| 変換ロジックを変更・追加 | `transformer.py`（`TextTransformer`） | 入出力の型は `types.py` の `SrcText` / `DstText` |
| 実行時パラメータを追加 | `context.py`（`TransformContext`） | 追加フィールドは呼び出し元（CLI 層）が組み立てて渡す |
| 変換結果に項目を追加 | `types.py`（`TransformResult`） | `orchestrator.py` の返却部分も合わせて変更する |
| I/O の実装を差し替え | `reader.py` / `writer.py` と `provider.py` | foundation の Protocol に準拠した実装を用意し、Provider で組み立て直す |
| 公開 API を追加 | `__init__.py` の `__all__` | 内部コンポーネントの公開は原則行わない |

## 7. 影響範囲

transform パッケージを変更した場合、以下の呼び出し元に影響が及ぶ。

| 呼び出し元 | ファイル | 影響する変更 |
|---|---|---|
| CLI の transform コマンド | `src/example/cli.py` | `TransformContext` のフィールド追加・変更、`TransformOrchestratorProvider` のインターフェース変更 |

## 8. 関連ドキュメント

- [transform パッケージ要件定義](./requirements.md): transform パッケージの機能要件や前提条件
- [Python アーキテクチャ設計](../../design/architecture.md): プロジェクト共通の設計思想
