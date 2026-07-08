from __future__ import annotations

from playwright.sync_api import Page


class BasePage:
    """Shared page plumbing. Playwright auto-waits on every action, so there are
    no implicit/global waits to configure — only the per-action default timeout,
    set once from config in conftest."""

    def __init__(self, page: Page, timeout_ms: int) -> None:
        self.page = page
        self.timeout_ms = timeout_ms

    def dismiss_consent(self) -> None:
        """Best-effort dismissal of a cookie/consent notice; no-op if absent."""
        for label in (
            "Accept",
            "OK",
            "Agree",
            "Принять",
            "Хорошо",
            "Согласен",
            "Понятно",
        ):
            button = self.page.get_by_role("button", name=label, exact=True)
            if button.count() and button.first.is_visible():
                try:
                    button.first.click()
                except Exception:
                    pass
                return
