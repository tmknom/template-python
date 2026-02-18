"""データモデル基盤の公開API(Foundation層)。

公開APIは `example.foundation.model` から import すること(`__all__` のみ互換性対象)。
"""

from example.foundation.model.base import CoreModel

__all__ = ["CoreModel"]
