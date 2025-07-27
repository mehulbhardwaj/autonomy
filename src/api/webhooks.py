from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Header, HTTPException, Request

from ..audit.logger import AuditLogger
from ..tasks.task_manager import TaskManager


class OverrideStore:
    """Simple append-only storage for webhook overrides."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def add(self, event: str, payload: dict[str, Any]) -> None:
        entry = {
            "event": event,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")


class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self, calls: int, period: float) -> None:
        self.calls = calls
        self.period = period
        self.timestamps: list[float] = []

    def allow(self) -> bool:
        now = time.monotonic()
        self.timestamps = [t for t in self.timestamps if now - t < self.period]
        if len(self.timestamps) >= self.calls:
            return False
        self.timestamps.append(now)
        return True


def verify_signature(secret: str, body: bytes, signature: str | None) -> bool:
    """Return True if signature matches the body using ``secret``."""
    if not secret:
        return True
    if not signature:
        return False
    mac = hmac.new(secret.encode(), msg=body, digestmod=hashlib.sha256)
    expected = "sha256=" + mac.hexdigest()
    return hmac.compare_digest(expected, signature)


def create_webhook_router(
    secret: str,
    store: OverrideStore,
    *,
    audit_logger: Optional["AuditLogger"] = None,
    rate_limit: int = 30,
    period: float = 60.0,
    task_manager: "TaskManager" | None = None,
) -> APIRouter:
    """Create a router handling GitHub webhooks."""
    logger = logging.getLogger(__name__)
    limiter = RateLimiter(rate_limit, period)

    router = APIRouter()

    @router.post("/webhook/github")
    async def github_webhook(
        request: Request,
        x_hub_signature_256: str | None = Header(None),
        x_github_event: str | None = Header(None),
    ) -> dict[str, bool]:
        if not limiter.allow():
            raise HTTPException(status_code=429, detail="Too many requests")
        body = await request.body()
        if not verify_signature(secret, body, x_hub_signature_256):
            raise HTTPException(status_code=400, detail="Invalid signature")
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid payload")
        event = x_github_event or "unknown"
        store.add(event, payload)
        if audit_logger:
            audit_logger.log("github_webhook", {"event": event})
        logger.info("GitHub webhook received: %s", event)
        if (
            task_manager
            and event == "issues"
            and payload.get("action") in {"edited", "labeled", "unlabeled"}
        ):
            task_manager._trigger_sync()
        return {"success": True}

    @router.post("/webhook/overrides")
    async def overrides_webhook(request: Request) -> dict[str, bool]:
        """Record manual override events."""
        if not limiter.allow():
            raise HTTPException(status_code=429, detail="Too many requests")
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid payload")
        store.add("override", payload)
        if audit_logger:
            audit_logger.log("manual_override", payload)
        logger.info("Override webhook received")
        if task_manager:
            task_manager._trigger_sync()
        return {"success": True}

    return router
