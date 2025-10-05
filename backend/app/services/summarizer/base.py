"""
Base interface for text summarization.
"""
from abc import ABC, abstractmethod


class SummarizerStrategy(ABC):
    """要約エンジンの基底クラス"""

    @abstractmethod
    async def summarize(self, text: str) -> str:
        """
        テキストを要約する

        Args:
            text: 要約対象のテキスト

        Returns:
            要約されたテキスト
        """
        pass
