import asyncio
from unittest.mock import patch

import pytest

from src.github.issue_manager import IssueManager

class DummyResponse:
    def __init__(self, num):
        self.status_code = 200
        self._num = num
    def json(self):
        return {"number": self._num}

class DummyClient:
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        pass
    async def get(self, url, headers=None):
        num = int(url.split("/")[-1])
        return DummyResponse(num)

@patch("src.github.issue_manager.httpx.AsyncClient", DummyClient)
@pytest.mark.asyncio
async def test_bulk_fetch_issues():
    mgr = IssueManager("t", "o", "r")
    results = await mgr.bulk_fetch_issues([1, 2, 3])
    assert [r["number"] for r in results] == [1, 2, 3]
