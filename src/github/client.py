"""HTTP client with retry and backoff for GitHub requests."""

from __future__ import annotations

import backoff
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class ResilientGitHubClient:
    """Simple HTTP client with retries and exponential backoff."""

    def __init__(self) -> None:
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    @backoff.on_exception(
        backoff.expo, requests.exceptions.RequestException, max_tries=3
    )
    def make_request(
        self, method: str, url: str, **kwargs
    ):  # pragma: no cover - simple wrapper
        return self.session.request(method, url, **kwargs)
