from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Language(Enum):
    En = "En"
    Ru = "Ru"


@dataclass(frozen=True)
class UiText:
    """Language-dependent bits. Most locators are language-independent (login by
    element id, the title is the page's only <textarea>, the body is the Draft.js
    div). Only the two publish buttons are text-matched, plus the context locale."""

    locale: str
    setup_and_publish: str
    publish: str

    @staticmethod
    def for_language(language: Language) -> "UiText":
        if language is Language.Ru:
            # Verified against the live Russian editor.
            return UiText(
                locale="ru-RU",
                setup_and_publish="Настроить и опубликовать",
                publish="Опубликовать",
            )
        # NOTE: EN labels are a best-effort translation of the verified RU labels;
        # the English editor is only reachable while logged in. Verify these two
        # strings on the first real English run and adjust if wording differs.
        return UiText(
            locale="en-US",
            setup_and_publish="Set up and publish",
            publish="Publish",
        )
