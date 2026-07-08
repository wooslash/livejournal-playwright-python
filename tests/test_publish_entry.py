from __future__ import annotations

import re

import allure
import pytest
from playwright.sync_api import Page

from pages.login_page import LoginPage
from pages.post_editor_page import PostEditorPage
from src.config import Config
from src.data_factory import for_author


@allure.feature("LiveJournal posting")
@pytest.mark.e2e
@pytest.mark.smoke
def test_login_and_publish_entry(page: Page, config: Config) -> None:
    post = for_author(config.author_name)

    with allure.step("Open login page"):
        login = LoginPage(page, config.timeout_ms).open()
        assert login.is_loaded(), "Login page did not load"

    with allure.step("Log in"):
        login.log_in(config.username, config.password)

    with allure.step("Open the post editor"):
        editor = PostEditorPage(page, config.timeout_ms).open()
        assert editor.is_loaded(), "Editor page did not load after login"

    with allure.step(f"Fill the entry (title = '{post.title}')"):
        editor.fill(post)

    with allure.step("Publish"):
        url = editor.publish_entry()

    # published entry URL, e.g. https://<user>.livejournal.com/373.html?newpost=1
    assert re.search(r"\.livejournal\.com/\d+\.html", url), f"Unexpected URL: {url}"
    allure.attach(url, name="entry-url", attachment_type=allure.attachment_type.TEXT)
