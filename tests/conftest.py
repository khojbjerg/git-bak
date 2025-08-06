from typing import Protocol
from unittest.mock import patch

import pytest

from git_bak.git import Git
from tests.utils.fakes import FakeRunner


class GitFactory(Protocol):
    def __call__(self, fail_on: str | None) -> Git: ...


@pytest.fixture
def make_git() -> GitFactory:
    def _make(fail_on: str | None) -> Git:
        runner = FakeRunner(fail_on=fail_on)
        return Git(runner)

    return _make


@pytest.fixture
def mock_now():
    with patch("git_bak.git.now", "20250101_101010"):
        yield
