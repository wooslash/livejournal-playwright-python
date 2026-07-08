from __future__ import annotations

import allure
import pytest

from src.config import Config


@pytest.fixture(scope="session")
def config() -> Config:
    return Config.load()


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, config: Config):
    """Force the UI language via locale and use a stable viewport."""
    return {
        **browser_context_args,
        "locale": config.ui.locale,
        "viewport": {"width": 1400, "height": 1000},
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args, config: Config):
    """Config-driven headless (pytest-playwright's --headed still overrides)."""
    return {**browser_type_launch_args, "headless": config.headless}


@pytest.fixture(autouse=True)
def _default_timeout(page, config: Config):
    """Set the per-action auto-wait ceiling — no implicit/global waits otherwise."""
    page.set_default_timeout(config.timeout_ms)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach a screenshot to Allure when a test fails."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page is not None:
            try:
                allure.attach(
                    page.screenshot(),
                    name="failure-screenshot",
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception:
                pass
