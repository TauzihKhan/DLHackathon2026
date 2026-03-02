from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


def _read_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _read_int(name: str, default: int, minimum: int, maximum: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return max(minimum, min(maximum, value))


def _read_float(name: str, default: float, minimum: float, maximum: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        value = float(raw)
    except ValueError:
        return default
    return max(minimum, min(maximum, value))


@dataclass(frozen=True)
class AISettings:
    """Runtime settings for Role 3 narrative generation."""

    role3_enabled: bool
    openai_api_key: str | None
    openai_model: str
    request_timeout_seconds: float
    temperature: float
    max_output_tokens: int
    practice_question_count: int

    @property
    def can_call_llm(self) -> bool:
        return self.role3_enabled and bool(self.openai_api_key)


@lru_cache(maxsize=1)
def get_ai_settings() -> AISettings:
    """Load and cache AI settings from environment variables."""

    return AISettings(
        role3_enabled=_read_bool("ROLE3_AI_ENABLED", True),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        request_timeout_seconds=_read_float("OPENAI_TIMEOUT_SECONDS", 12.0, 2.0, 60.0),
        temperature=_read_float("ROLE3_AI_TEMPERATURE", 0.2, 0.0, 1.0),
        max_output_tokens=_read_int("ROLE3_MAX_OUTPUT_TOKENS", 600, 128, 2000),
        practice_question_count=_read_int("ROLE3_PRACTICE_QUESTION_COUNT", 3, 1, 5),
    )

