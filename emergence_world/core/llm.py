"""Unified LLM client — OpenAI API format with multi-provider support."""

import asyncio
import logging
from typing import Any

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from emergence_world.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class LLMClient:
    """Async LLM client using OpenAI API format."""

    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            timeout=60.0,
        )
        self._default_model = settings.llm_default_model

    async def chat_completion(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        model: str | None = None,
    ) -> ChatCompletion:
        """Call LLM with retry logic."""
        target_model = model or self._default_model
        last_error: Exception | None = None

        for attempt in range(3):
            try:
                kwargs: dict[str, Any] = {
                    "model": target_model,
                    "messages": messages,
                }
                if tools:
                    kwargs["tools"] = tools
                    kwargs["tool_choice"] = "auto"

                response = await self._client.chat.completions.create(**kwargs)
                return response

            except Exception as e:
                last_error = e
                wait = 2 ** attempt
                logger.warning(f"LLM call failed (attempt {attempt + 1}/3): {e}, retrying in {wait}s")
                await asyncio.sleep(wait)

        raise RuntimeError(f"LLM call failed after 3 attempts: {last_error}")

    async def close(self) -> None:
        await self._client.close()
