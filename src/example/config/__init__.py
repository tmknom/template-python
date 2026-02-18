"""設定管理の公開API。

公開APIは `example.config` から import すること(`__all__` のみ互換性対象)。
"""

from example.config.path import PathConfig

__all__ = [
    "PathConfig",
]
