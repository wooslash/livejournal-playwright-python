from __future__ import annotations

import re
from collections.abc import Callable

from playwright.sync_api import Page, expect

from pages.base_page import BasePage
from src.data_factory import PostData
from src.localization import Language, UiText


def _any_label(pick: Callable[[UiText], str]) -> re.Pattern[str]:
    """Regex matching a label in any supported language. A logged-in editor
    renders in the account's interface language, which need not match the
    configured LANGUAGE, so publish buttons are matched across all languages."""
    labels = {pick(UiText.for_language(lang)) for lang in (Language.En, Language.Ru)}
    return re.compile(r"^(?:%s)$" % "|".join(re.escape(t) for t in labels))


class PostEditorPage(BasePage):
    """The modern React/Draft.js editor. /update.bml redirects here (/post/).
    Title and body locators are language-independent; the publish buttons are
    matched across all supported languages' labels."""

    URL = "https://www.livejournal.com/update.bml"

    def __init__(self, page: Page, timeout_ms: int) -> None:
        super().__init__(page, timeout_ms)
        # The editor page has exactly one <textarea> (the title) and one Draft.js body.
        self.title = page.locator("textarea")
        self.body = page.locator("div.public-DraftEditor-content")
        self.setup_and_publish = page.get_by_role(
            "button", name=_any_label(lambda u: u.setup_and_publish)
        )
        self.publish = page.get_by_role("button", name=_any_label(lambda u: u.publish))

    def open(self) -> "PostEditorPage":
        self.page.goto(self.URL)
        expect(self.title).to_be_visible(timeout=self.timeout_ms)
        self._dismiss_draft_modal()
        return self

    def _dismiss_draft_modal(self) -> None:
        # If a previous session left a draft, LiveJournal shows a "restore last
        # draft?" modal that covers the editor and intercepts clicks. Its close
        # control has a language-independent aria-label; Escape closes react-modal.
        close = self.page.locator("button[aria-label='Modal Window Close']").first
        try:
            close.wait_for(state="visible", timeout=4000)
        except Exception:
            return
        self.page.keyboard.press("Escape")
        close.wait_for(state="hidden", timeout=self.timeout_ms)

    def is_loaded(self) -> bool:
        return (
            "/post" in self.page.url
            and self.title.is_visible()
            and self.body.is_visible()
        )

    def fill(self, post: PostData) -> "PostEditorPage":
        self.title.fill(post.title)
        # Draft.js body is a contenteditable div — focus it and type via the
        # keyboard so the editor records real input events.
        self.body.click()
        self.page.keyboard.type(post.body)
        return self

    def publish_entry(self) -> str:
        self.setup_and_publish.click()
        self.publish.click()
        # On success LiveJournal redirects to the entry, e.g.
        # https://<user>.livejournal.com/373.html?newpost=1 (note the query string).
        expect(self.page).to_have_url(
            re.compile(r"https://.*\.livejournal\.com/\d+\.html"),
            timeout=self.timeout_ms,
        )
        return self.page.url
