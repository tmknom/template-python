"""共有 Fake 実装パッケージ"""

from tests.fake.fs import InMemoryFsReader, InMemoryFsWriter

__all__ = [
    "InMemoryFsReader",
    "InMemoryFsWriter",
]
