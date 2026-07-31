from __future__ import annotations

import os

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from pydantic import BaseModel


def get_llm() -> BaseChatModel:
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    return ChatOpenAI(model=model, temperature=0.7)


def structured_llm(schema: type[BaseModel]) -> Runnable:
    """Structured assistant output via OpenAI json_schema (strict), not tool calling."""
    return get_llm().with_structured_output(
        schema,
        method="json_schema",
        strict=True,
    )
