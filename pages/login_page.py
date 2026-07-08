from __future__ import annotations

import re

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class LoginPage(BasePage):
    """The native username/password form at /login.bml.
    All locators are language-independent (element ids and a CSS class)."""

    URL = "https://www.livejournal.com/login.bml"

    def __init__(self, page: Page, timeout_ms: int) -> None:
        super().__init__(page, timeout_ms)
        self.user = page.locator("input#user")
        self.password = page.locator("input#lj_loginwidget_password")
        # --auth is unique to the password-login button; --login also matches the
        # OpenID button (permanently --disabled), which breaks the readiness check.
        self.submit = page.locator("button.b-loginform-btn--auth")

    def open(self) -> "LoginPage":
        self.page.goto(self.URL)
        self.dismiss_consent()
        expect(self.user).to_be_visible(timeout=self.timeout_ms)
        return self

    def is_loaded(self) -> bool:
        return (
            "login.bml" in self.page.url
            and self.user.is_visible()
            and self.password.is_visible()
        )

    def log_in(self, username: str, password: str) -> None:
        self.user.fill(username)
        self.password.fill(password)

        # The submit button is gated by a CSS class ('--disabled'), not the HTML
        # disabled attribute, and only clears once the credentials validate. If it
        # never clears, the input was rejected — most commonly an email was given
        # instead of the LiveJournal username. Fail fast with a clear message.
        try:
            expect(self.submit).not_to_have_class(
                re.compile("--disabled"), timeout=self.timeout_ms
            )
        except AssertionError as exc:
            raise RuntimeError(
                "Login form did not accept the input (submit stayed disabled). "
                "Check LJ_USERNAME — LiveJournal expects the account username, not an email."
            ) from exc

        self.submit.click()
        # Success = the login form is gone. On success LiveJournal may stay on
        # /login.bml and render a "you are logged in" interstitial instead of
        # redirecting, so wait for the login button to detach rather than for a
        # URL change. Wrong credentials re-render the form → this times out.
        expect(self.submit).to_have_count(0, timeout=self.timeout_ms)
