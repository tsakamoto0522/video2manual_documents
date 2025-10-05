"""
OpenAI GPT-based text summarization.
"""
import asyncio
from typing import Optional

from openai import AsyncOpenAI

from app.core import logger, settings

from .base import SummarizerStrategy


class OpenAISummarizer(SummarizerStrategy):
    """OpenAI GPTを使用したテキスト要約"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize OpenAI Summarizer.

        Args:
            api_key: OpenAI API key (デフォルトは設定から取得)
            model: GPTモデル名 (デフォルトは設定から取得)
        """
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_model

        if not self.api_key:
            raise ValueError("OpenAI APIキーが設定されていません。環境変数OPENAI_API_KEYを設定してください。")

        self.client = AsyncOpenAI(api_key=self.api_key)

    async def summarize(self, text: str) -> str:
        """
        テキストを要約する

        Args:
            text: 要約対象のテキスト

        Returns:
            要約されたテキスト
        """
        logger.info(f"Starting text summarization using {self.model}")

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "あなたは動画マニュアルの文字起こしテキストを要約する専門家です。"
                            "以下のルールに従って要約してください：\n"
                            "1. 手順や操作の流れを明確に保つ\n"
                            "2. 重要な用語や固有名詞はそのまま残す\n"
                            "3. 冗長な表現を削除し、簡潔にまとめる\n"
                            "4. 箇条書きや段落を使って読みやすくする"
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"以下のテキストを要約してください：\n\n{text}",
                    },
                ],
                temperature=0.3,
                max_tokens=2000,
            )

            summary = response.choices[0].message.content
            logger.info("Text summarization completed successfully")

            return summary if summary else ""

        except Exception as e:
            logger.error(f"OpenAI summarization failed: {e}")
            raise Exception(f"要約処理に失敗しました: {e}")
