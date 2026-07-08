from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from src.localization import Language, UiText

load_dotenv()


@dataclass(frozen=True)
class Config:
    """Run config from environment / .env. Browser is chosen via the pytest
    `--browser` flag (chromium|firefox|webkit), not here."""

    username: str
    password: str
    author_name: str
    language: Language
    headless: bool
    timeout_ms: int

    @property
    def ui(self) -> UiText:
        return UiText.for_language(self.language)

    @staticmethod
    def load() -> "Config":
        return Config(
            username=_require("LJ_USERNAME"),
            password=_require("LJ_PASSWORD"),
            author_name=os.getenv("POST_TITLE") or "Dmitriy Shin",
            language=_language(os.getenv("LANGUAGE") or "En"),
            headless=(os.getenv("HEADLESS") or "false").strip().lower() == "true",
            timeout_ms=_int(os.getenv("TIMEOUT_SECONDS"), 30) * 1000,
        )


def _language(raw: str) -> Language:
    try:
        return Language(raw.strip().capitalize())
    except ValueError:
        return Language.En


def _int(raw: str | None, fallback: int) -> int:
    try:
        value = int(raw) if raw is not None else fallback
        return value if value > 0 else fallback
    except ValueError:
        return fallback


def _require(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise RuntimeError(
            f"Missing required credential '{key}'. Copy .env.example to .env and fill it in."
        )
    return value
