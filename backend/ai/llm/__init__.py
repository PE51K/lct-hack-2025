"""
LLM Module.

This module initializes the language model used by the application,
configured for YandexGPT integration.
"""

import sys

from langchain_openai import ChatOpenAI

sys.path.insert(0, "..")

from core.settings import settings

# Initialize the base language model using YandexGPT
llm = ChatOpenAI(
    api_key=settings.ai.yandex_gpt.api_key,
    base_url=settings.ai.yandex_gpt.base_url,
    model_name=settings.ai.yandex_gpt.model_name,
)
