from langchain_openai import ChatOpenAI

from app.core.config import get_settings


def get_llm(
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> ChatOpenAI:
    settings = get_settings()

    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        temperature=temperature if temperature is not None else settings.default_temperature,
        timeout=settings.llm_timeout_seconds,
        max_retries=0,
        max_tokens=max_tokens if max_tokens is not None else settings.llm_default_max_tokens,
    )