#!/usr/bin/env bash
# Run the suite, then render and open the Allure report in the browser.
# Any extra arguments pass through to `pytest`, e.g.:
#   ./run.sh --browser firefox -m smoke
# `allure serve` (Allure CLI, `brew install allure`) opens the report automatically.

pytest --alluredir=allure-results "$@"
allure serve allure-results
