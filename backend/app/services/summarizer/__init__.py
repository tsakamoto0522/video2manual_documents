"""
Text summarization services.
"""
from .base import SummarizerStrategy
from .openai_summarizer import OpenAISummarizer

__all__ = ["SummarizerStrategy", "OpenAISummarizer"]


def get_summarizer() -> SummarizerStrategy:
    """要約エンジンのインスタンスを取得"""
    return OpenAISummarizer()
