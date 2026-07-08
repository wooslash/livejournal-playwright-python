# LiveJournal E2E — Python / Playwright / pytest
# Official Playwright image ships the browser engines for this version.
FROM mcr.microsoft.com/playwright/python:v1.61.0-jammy

WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir \
    pytest playwright pytest-playwright faker allure-pytest python-dotenv
COPY . .

# Headless in a container; credentials come from `docker run --env-file .env`.
ENV HEADLESS=true
ENTRYPOINT ["pytest"]
CMD ["--alluredir=allure-results"]
