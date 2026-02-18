"""テキスト変換の中核処理

行番号付与と日時ヘッダー追加を担当する。
"""

from datetime import datetime

from example.foundation.log import log


class TextTransformer:
    """テキストに行番号と日時ヘッダーを付与する

    入力テキストの各行に行番号を付与し、先頭に現在日時を追加する。
    """

    def __init__(self) -> None:
        """TextTransformerを初期化"""

    @log
    def transform(self, text: str, current_datetime: datetime) -> str:
        """テキストに行番号と日時ヘッダーを付与

        Args:
            text: 変換対象のテキスト
            current_datetime: 先頭に付与する日時

        Returns:
            日時ヘッダーと行番号を付与したテキスト
        """
        # 各行に行番号を付与
        lines = text.splitlines()
        numbered_lines = [f"{i + 1}: {line}" for i, line in enumerate(lines)]

        # 先頭に現在日時を追加
        output_lines = [str(current_datetime), *numbered_lines]

        # 改行区切りのテキストに戻す
        return "\n".join(output_lines)
