"""共有 Fake 実装パッケージ"""

from tests.unit.fake.fs import InMemoryFsReader, InMemoryFsWriter

__all__ = [
    "InMemoryFsReader",
    "InMemoryFsWriter",
]
