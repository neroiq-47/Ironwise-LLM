"""Runtime configuration, read from environment variables (12-factor style)."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

log = logging.getLogger("ironwise.config")


class ConfigError(ValueError):
    """An IRONWISE_* environment variable has an invalid value."""


def _env(name: str, default: str) -> str:
    return os.environ.get(name, default)


def _num(name: str, default: str, kind: type[int] | type[float]) -> Any:
    raw = _env(name, default)
    try:
        return kind(raw)
    except ValueError as exc:
        raise ConfigError(f"{name}={raw!r} is not a valid {kind.__name__}") from exc


@dataclass(frozen=True)
class Settings:
    """All tunables in one place. Every field maps to a IRONWISE_* env var."""

    db_path: Path = field(
        default_factory=lambda: Path(_env("IRONWISE_DB_PATH", "data/ironwise.db"))
    )
    audit_path: Path = field(
        default_factory=lambda: Path(_env("IRONWISE_AUDIT_PATH", "data/audit.jsonl"))
    )
    llm_backend: str = field(default_factory=lambda: _env("IRONWISE_LLM_BACKEND", "openai"))
    llm_base_url: str = field(
        default_factory=lambda: _env("IRONWISE_LLM_BASE_URL", "http://localhost:8080/v1")
    )
    llm_model: str = field(default_factory=lambda: _env("IRONWISE_LLM_MODEL", "ironwise-8b-q4"))
    llm_timeout_s: float = field(
        default_factory=lambda: _num("IRONWISE_LLM_TIMEOUT_S", "60", float)
    )
    api_key: str = field(default_factory=lambda: _env("IRONWISE_API_KEY", ""))
    max_rows: int = field(default_factory=lambda: _num("IRONWISE_MAX_ROWS", "500", int))
    max_upload_bytes: int = field(
        default_factory=lambda: _num("IRONWISE_MAX_UPLOAD_BYTES", str(25 * 1024 * 1024), int)
    )
    redact_pii: bool = field(
        default_factory=lambda: _env("IRONWISE_REDACT_PII", "true").lower() in {"1", "true", "yes"}
    )
    query_timeout_s: float = field(
        default_factory=lambda: _num("IRONWISE_QUERY_TIMEOUT_S", "10", float)
    )

    def __post_init__(self) -> None:
        if not 1 <= self.max_rows <= 100_000:
            raise ConfigError("IRONWISE_MAX_ROWS must be between 1 and 100000")
        if self.max_upload_bytes < 1:
            raise ConfigError("IRONWISE_MAX_UPLOAD_BYTES must be positive")
        if self.llm_timeout_s <= 0 or self.query_timeout_s <= 0:
            raise ConfigError("timeouts must be positive")
        if self.api_key and len(self.api_key) < 16:
            log.warning("IRONWISE_API_KEY is shorter than 16 characters; use a long random key")


def get_settings() -> Settings:
    return Settings()
