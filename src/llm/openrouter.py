import os
from typing import Any, Dict, List, Optional

import httpx


class OpenRouterError(Exception):
    """Raised when OpenRouter request fails."""


class OpenRouterClient:
    """Simple OpenRouter API client with fallback and cost tracking."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://openrouter.ai/api/v1",
    ) -> None:
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(timeout=15.0)
        self.costs: Dict[str, Dict[str, int]] = {}

    def _record_cost(self, operation: str, usage: Dict[str, Any]) -> None:
        entry = self.costs.setdefault(
            operation, {"prompt_tokens": 0, "completion_tokens": 0}
        )
        entry["prompt_tokens"] += usage.get("prompt_tokens", 0)
        entry["completion_tokens"] += usage.get("completion_tokens", 0)

    # ------------------------------------------------------------------
    def complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        operation: str = "default",
        **params: Any,
    ) -> str:
        """Call the OpenRouter API or return a stubbed response."""
        if not self.api_key:
            # In tests or local dev without API key we just echo back
            content = messages[-1].get("content", "") if messages else ""
            return f"LLM:{content}"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/mehulbhardwaj/autonomy",
            "X-Title": "Autonomy",
        }
        payload = {"model": model, "messages": messages}
        payload.update(params)
        try:
            resp = self._client.post(
                f"{self.base_url}/chat/completions", json=payload, headers=headers
            )
            resp.raise_for_status()
            data = resp.json()
            self._record_cost(operation, data.get("usage", {}))
            return data["choices"][0]["message"]["content"]
        except Exception as exc:  # pragma: no cover - network failure edge
            raise OpenRouterError(str(exc)) from exc

    def complete_with_fallback(
        self,
        messages: List[Dict[str, str]],
        models: List[str],
        operation: str = "default",
        **params: Any,
    ) -> str:
        last_error: Optional[Exception] = None
        for model in models:
            try:
                return self.complete(
                    messages, model=model, operation=operation, **params
                )
            except OpenRouterError as exc:
                last_error = exc
        raise last_error if last_error else OpenRouterError("No models provided")


class ModelSelector:
    """Very small helper to choose models for operations."""

    def __init__(self, mapping: Optional[Dict[str, List[str]]] = None) -> None:
        self.mapping = mapping or {
            "analysis": ["anthropic/claude-3.5-sonnet", "openai/gpt-4o"],
            "ranking": ["openai/gpt-4o-mini", "anthropic/claude-3-haiku"],
            "decomposition": ["anthropic/claude-3.5-sonnet", "openai/gpt-4o"],
            "planning": ["openai/gpt-4o-mini", "openai/gpt-4o"],
        }

    def get(self, operation: str) -> List[str]:
        return self.mapping.get(operation, ["openai/gpt-4o"])
