from typing import Iterable

import pytest

from src.github.pat_scopes import (
    REQUIRED_GITHUB_SCOPES,
    get_github_token_scopes,
    validate_github_token_scopes,
)


class DummyResponse:
    def __init__(self, status_code: int, scopes: str):
        self.status_code = status_code
        self.headers = {"X-OAuth-Scopes": scopes}


def dummy_get(url: str, headers=None, timeout=10):
    return DummyResponse(200, "repo, read:org, write:repo_hook, read:user")


def test_get_github_token_scopes(monkeypatch):
    monkeypatch.setattr("requests.get", dummy_get)
    scopes = get_github_token_scopes("token")
    assert set(scopes) == set(REQUIRED_GITHUB_SCOPES)


def test_validate_github_token_scopes(monkeypatch):
    monkeypatch.setattr("requests.get", dummy_get)
    validate_github_token_scopes("token")

    def bad_get(url: str, headers=None, timeout=10):
        return DummyResponse(200, "repo")

    monkeypatch.setattr("requests.get", bad_get)
    with pytest.raises(ValueError):
        validate_github_token_scopes("token")
