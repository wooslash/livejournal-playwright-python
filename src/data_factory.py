from __future__ import annotations

from dataclasses import dataclass

from faker import Faker

_faker = Faker("en_US")


@dataclass(frozen=True)
class PostData:
    title: str
    body: str


def for_author(author_name: str) -> PostData:
    """Title = author name; body generated fresh and unique per call."""
    body = (
        "\n\n".join(_faker.paragraphs(nb=2))
        + f"\n\nAutomated Playwright run — {_faker.uuid4()}"
    )
    return PostData(title=author_name, body=body)
