import sys

from langchain_openai import ChatOpenAI

sys.path.insert(0, "..")

from core.settings import settings


# Set up the base language model (YandexGPT)
llm = ChatOpenAI(
    api_key=settings.ai.yandex_gpt.api_key,
    base_url=settings.ai.yandex_gpt.base_url,
    model_name=settings.ai.yandex_gpt.model_name,
)
