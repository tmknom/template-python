# foundation/fs パッケージ基本設計

[foundation/fs パッケージ要件定義](./requirements.md) に基づいた基本設計を説明します。

## アーキテクチャパターン

- **読み書き分離パターン**: `TextFileSystemReader` と `TextFileSystemWriter` を独立したクラスとして定義し、呼び出し元が必要な機能だけに依存できるようにする
- **Protocol パターン**: Python の `typing.Protocol` を使って構造的部分型（ダックタイピング）ベースのインターフェースを定義し、実装クラスへの明示的な継承なしに型安全な依存性注入を実現する。副作用を持つ処理（ファイル I/O）とそれを利用するビジネスロジックの間に境界を設けることで、副作用の範囲をコントロールする
- **エラー変換パターン**: OS 由来の例外を catch し、`FileSystemError` に変換して再送出することで、呼び出し元が処理すべき例外型を統一する

## コンポーネント構成

### 主要コンポーネント

| コンポーネント | クラス名 | 役割 |
|---|---|---|
| 読み取り実装クラス | `TextFileSystemReader` | テキストファイルを UTF-8 で読み込み文字列を返す |
| 書き込み実装クラス | `TextFileSystemWriter` | テキスト内容を UTF-8 でファイルに書き込む（親ディレクトリ自動作成付き） |
| 読み取りプロトコル | `TextFileSystemReaderProtocol` | 読み取り操作の型安全なインターフェース定義 |
| 書き込みプロトコル | `TextFileSystemWriterProtocol` | 書き込み操作の型安全なインターフェース定義 |
| ファイルシステム例外 | `FileSystemError` | ファイル操作エラーを表す業務例外クラス |

### ファイルレイアウト

#### プロダクションコード

```bash
src/example/foundation/fs/
├── __init__.py    # 公開 API の定義（5 シンボルを __all__ で明示）
├── error.py       # FileSystemError（ファイルシステム固有の業務例外）
├── protocol.py    # TextFileSystemReaderProtocol / TextFileSystemWriterProtocol
└── text.py        # TextFileSystemReader / TextFileSystemWriter（実装クラス）
```

#### テストコード

```bash
tests/unit/test_foundation/test_fs/
└── test_text.py    # TextFileSystemReader / TextFileSystemWriter のテスト
```

## 処理フロー

### 読み取りフロー

1. 呼び出し元からファイルパスを受け取る
2. ファイルを UTF-8 で読み込み、内容を文字列として返す
3. 読み取り失敗時はアプリケーション共通の例外型に変換して送出する

### 書き込みフロー

1. 呼び出し元からテキストとファイルパスを受け取る
2. 書き込み先の親ディレクトリが存在しない場合は自動作成する
3. ファイルに上書き書き込みする
4. いずれかのステップで失敗した場合はアプリケーション共通の例外型に変換して送出する

## 固有の設計判断

### 読み取りと書き込みの分離

**設計の意図**: `TextFileSystemReader` と `TextFileSystemWriter` を 1 つのクラスにまとめず、読み取り専用・書き込み専用として独立して定義している。

**なぜそう設計したか**: 呼び出し元のコンポーネントが必要とするのは多くの場合、読み取りか書き込みのどちらか一方である。単一クラスに両方の機能を集約すると、書き込み不要のコンポーネントにも書き込み機能への依存が生まれ、最小権限の原則に反する。Protocol も読み取り・書き込みで個別に定義することで、呼び出し元が必要な機能のみに依存できるようになる。

**トレードオフ**: 両方の操作が必要な呼び出し元では 2 つのオブジェクトを管理する必要がある。ただし、読み書きを同時に必要とするケースは読み書きの責務分離の観点から再設計を検討する余地がある。

### Protocol による抽象化

**設計の意図**: 実装クラス（`TextFileSystemReader`, `TextFileSystemWriter`）とは別に、Protocol インターフェース（`TextFileSystemReaderProtocol`, `TextFileSystemWriterProtocol`）を定義し、副作用を持つ処理（実装クラス）と副作用を持たない処理（呼び出し元のビジネスロジック）の間に明確な境界を設ける。

**なぜそう設計したか**: ファイルシステムへのアクセスはアプリケーション外への副作用を持つ処理である。副作用を Protocol 境界に閉じ込め、呼び出し元は Protocol にのみ依存させることで、2 つの効果が得られる。

第一に、開発時の認知負荷の低減。呼び出し元コンポーネントは「Protocol を満たすオブジェクトを受け取る」だけであり、その実装が実際にファイルシステムにアクセスするかどうかを意識する必要がない。

第二に、テスタビリティの大幅な向上。呼び出し元のテストでは、Protocol に準拠したインメモリ実装（読み取り結果を固定文字列で返すクラス、書き込み内容をフィールドに保持するクラスなど）を作成し、テスト対象に注入するだけでよい。インメモリ実装は通常の Python クラスとして記述でき、モックフレームワーク固有の知識（動的パッチングや呼び出し検証の専用 API 等）が不要である。実装の変更に追従して Fake クラスを更新する際も、通常のリファクタリングとして扱える。

Python の `typing.Protocol` は構造的部分型をサポートするため、実装クラスが明示的に Protocol を継承しなくても型チェックが機能する。インメモリ実装（Fake）を作る際も同様で、明示的な継承なしに Protocol の要件を満たすクラスを書くだけでよい。

**トレードオフ**: 実装クラスと Protocol の両方を定義・維持する必要があり、インターフェース変更時は両方を更新しなければならない。また、Protocol に準拠したインメモリ実装（Fake）もシグネチャ変更に追従して更新が必要になる。

### OS 例外の FileSystemError への変換

**設計の意図**: `FileNotFoundError`, `PermissionError`, `IsADirectoryError` などの OS 由来の例外を catch し、`FileSystemError` に変換して送出している。

**なぜそう設計したか**: 呼び出し元が処理すべき例外が複数の OS 固有例外に分散すると、抜け漏れが起きやすい。`FileSystemError` という単一の型に統一することで、呼び出し元は 1 種類の例外を処理するだけで済む。また、`FileSystemError` は `ApplicationError` を継承しているため、アプリケーション全体のエラーハンドリング基盤（`ErrorHandler`）でそのまま処理できる。

**トレードオフ**: OS 例外の種類（ファイルが見つからない vs 権限不足）に応じて呼び出し元が異なる回復処理を行いたい場合、`FileSystemError` のメッセージから種別を判断するか、`cause` フィールドを参照する必要がある。現状は例外の種別をサブクラスで分離していない。

### 書き込み時の親ディレクトリ自動作成

**設計の意図**: `TextFileSystemWriter.write()` は書き込み前に親ディレクトリを再帰的に作成する（`parents=True, exist_ok=True`）。

**なぜそう設計したか**: 書き込み先ディレクトリが存在するかどうかの確認と作成を呼び出し元が毎回実装するのは定型的な前処理であり、ファイル書き込みの責務に含めるのが自然である。自動作成によって呼び出し元の前処理コードが不要になり、呼び出し側のコードが簡潔になる。

**トレードオフ**: 意図しないディレクトリが自動作成される可能性がある。ただし、書き込みパスは呼び出し元が明示的に指定するため、意図しないパスへの書き込みが発生するリスクは呼び出し元の責任範囲となる。

## 制約と注意点

### エンコーディングは UTF-8 固定

`TextFileSystemReader` と `TextFileSystemWriter` はいずれも UTF-8 エンコーディングを使用する。UTF-8 以外のエンコーディングが必要な場合は別途実装を用意すること。

### 書き込みは上書きモード

`TextFileSystemWriter` は既存ファイルへの書き込み時に内容を上書きする（追記モードではない）。追記が必要な場合は別途実装を用意すること。

### 公開 API の制限

公開 API は `__init__.py` の `__all__` で定義された 5 シンボルのみ（`FileSystemError`, `TextFileSystemReader`, `TextFileSystemReaderProtocol`, `TextFileSystemWriter`, `TextFileSystemWriterProtocol`）。内部モジュールからの直接 import は行わず、`example.foundation.fs` パッケージから import すること。

### FileSystemError の例外チェーン

`FileSystemError` の送出時には元の OS 例外を `cause` フィールドおよび Python の `from e` 構文で例外チェーンに保持する。スタックトレースや `cause` を参照することで、元の OS レベルのエラー内容を確認できる。

## 外部依存と拡張性

### 外部システム依存

| 依存先 | 用途 |
|---|---|
| Python `pathlib.Path` 標準ライブラリ | ファイルシステム操作（読み取り・書き込み・ディレクトリ作成） |
| foundation/error パッケージ `ApplicationError` | `FileSystemError` の基底クラス |

### 想定される拡張ポイント

- `TextFileSystemReaderProtocol` / `TextFileSystemWriterProtocol` に準拠したクラスを実装することで、インメモリファイルシステムやクラウドストレージなど、実際のファイルシステム以外のバックエンドに切り替えられる
- `FileSystemError` をサブクラス化（例: `FileNotFoundError`, `PermissionDeniedError`）することで、エラー種別ごとに異なる回復処理を呼び出し元で実装できるようになる
- バイナリファイルの読み書きが必要になった場合は、同様の設計パターンで `BinaryFileSystemReader` / `BinaryFileSystemWriter` を追加できる

### 拡張時の注意点

- Protocol インターフェースのシグネチャを変更する場合、Protocol に準拠している既存の実装クラスも合わせて更新すること
- `TextFileSystemWriter` の自動ディレクトリ作成の挙動を変更する場合は、呼び出し元のコードが前処理なしでファイル書き込みを呼んでいることを考慮すること

## 変更パターン別ガイド

よくある変更ケースと、対応するファイルの道筋を示す。

| 変更内容 | 主な変更対象 | 備考 |
|---|---|---|
| 読み取りロジックを変更 | `text.py`（`TextFileSystemReader`） | Protocol のシグネチャを変更する場合は `protocol.py` も更新する |
| 書き込みロジックを変更 | `text.py`（`TextFileSystemWriter`） | Protocol のシグネチャを変更する場合は `protocol.py` も更新する |
| エラーメッセージを変更 | `text.py`（各 except ブロック） | `FileSystemError` のコンストラクタ引数（`message`, `cause`）を確認する |
| 新しいバックエンド実装を追加 | 新規ファイル（Protocol に準拠したクラスを定義） | `__init__.py` の `__all__` への追加は公開 API として必要な場合のみ |
| 公開 API を追加 | `__init__.py` の `__all__` | 内部コンポーネントの公開は原則行わない |

## 影響範囲

foundation/fs パッケージはアプリケーション全体のファイルシステム操作基盤であり、公開 API を変更した場合はコードベース全体に影響が及ぶ。Protocol インターフェースのシグネチャを変更すると、そのインターフェースに依存するすべてのパッケージで実装の更新が必要になる。呼び出し元はコードベース全体に及ぶため、変更時は全パッケージへの影響を確認すること。

## 関連ドキュメント

- [foundation/fs パッケージ要件定義](./requirements.md): foundation/fs パッケージの機能要件や前提条件
- [foundation/error パッケージ基本設計](../error/design.md): foundation/error パッケージのアーキテクチャ設計やコンポーネント構成
- [Python アーキテクチャ設計](../../../design/architecture.md): プロジェクト共通の設計思想
