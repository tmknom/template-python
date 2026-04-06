"""共有 Fake 実装パッケージ"""

# Fake は他のテストパッケージからインポートされるライブラリとして機能するため、
# __init__.py で re-export を行う必要があり、空ファイルにできない。
# paladin: ignore-file[require-empty-test-init]
from tests.fake.fs import InMemoryFsReader, InMemoryFsWriter

__all__ = [
    "InMemoryFsReader",
    "InMemoryFsWriter",
]
