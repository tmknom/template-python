"""Transform向けドメインモデル定義"""

from dataclasses import dataclass
from typing import NewType

SrcText = NewType("SrcText", str)
"""ソーステキスト"""

DstText = NewType("DstText", str)
"""デスティネーションテキスト"""


@dataclass(frozen=True)
class TransformResult:
    """Transform実行結果

    Transform処理全体の結果を保持します。
    """

    length: int
    """変換したテキストの行数"""
