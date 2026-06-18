"""Unified LLM client — Anthropic API format."""

import asyncio
import logging
from typing import Any

from anthropic import AsyncAnthropic

from emergence_world.backend.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class LLMClient:
    """Async LLM client using Anthropic API."""

    def __init__(self) -> None:
        self._client = AsyncAnthropic(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            timeout=60.0,
        )
        self._default_model = settings.llm_default_model
        self._max_tokens = settings.llm_max_tokens

    async def chat_completion(
        self,
        system: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        model: str | None = None,
    ) -> Any:
        """Call LLM with Anthropic API format. Returns the Message object."""
        target_model = model or self._default_model
        last_error: Exception | None = None

        for attempt in range(3):
            try:
                kwargs: dict[str, Any] = {
                    "model": target_model,
                    "max_tokens": self._max_tokens,
                    "system": system,
                    "messages": messages,
                }
                if tools:
                    kwargs["tools"] = tools

                response = await self._client.messages.create(**kwargs)
                return response

            except Exception as e:
                last_error = e
                wait = 2 ** attempt
                logger.warning(f"LLM call failed (attempt {attempt + 1}/3): {e}, retrying in {wait}s")
                await asyncio.sleep(wait)

        raise RuntimeError(f"LLM call failed after 3 attempts: {last_error}")

    async def close(self) -> None:
        await self._client.close()
