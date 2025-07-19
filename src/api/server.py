from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from ..audit.logger import AuditLogger
from ..audit.undo import UndoManager
from ..github.issue_manager import IssueManager
from ..tasks.backlog_doctor import BacklogDoctor
from ..tasks.task_manager import TaskManager


class UpdateTaskRequest(BaseModel):
    status: Optional[str] = None
    done: bool = False
    notes: Optional[str] = None


def create_app(
    issue_manager: IssueManager,
    audit_logger: Optional[AuditLogger] = None,
) -> FastAPI:
    """Return a FastAPI app wired with core managers."""

    task_manager = TaskManager.__new__(TaskManager)
    task_manager.issue_manager = issue_manager
    from ..tasks.pinned_items import PinnedItemsStore

    task_manager.pinned_store = PinnedItemsStore()
    task_manager.project_id = f"{issue_manager.owner}/{issue_manager.repo}"
    backlog_doctor = BacklogDoctor(issue_manager)
    audit_logger = audit_logger or AuditLogger(Path("audit.log"))
    undo_manager = UndoManager(issue_manager, audit_logger)

    app = FastAPI(title="Autonomy API", version="1.0")

    # ------------------------------ Tasks ------------------------------
    @app.get("/api/v1/tasks/next")
    def get_next_task(assignee: Optional[str] = None, team: Optional[str] = None):
        issue = task_manager.get_next_task(assignee=assignee, team=team)
        if not issue:
            raise HTTPException(status_code=404, detail="No tasks found")
        return issue

    @app.get("/api/v1/tasks")
    def list_tasks(
        assignee: Optional[str] = None,
        team: Optional[str] = None,
        limit: int = 10,
    ):
        return task_manager.list_tasks(assignee=assignee, team=team, limit=limit)

    @app.post("/api/v1/tasks/{issue_id}/update")
    def update_task(issue_id: int, payload: UpdateTaskRequest):
        success = task_manager.update_task(
            issue_id,
            status=payload.status,
            done=payload.done,
            notes=payload.notes,
        )
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update task")
        return {"success": True}

    # --------------------------- Backlog Doctor ---------------------------
    @app.post("/api/v1/backlog/doctor/run")
    def run_backlog_doctor(
        stale_days: int = 14,
        checklist_limit: int = 10,
    ):
        return backlog_doctor.run(
            stale_days=stale_days,
            checklist_limit=checklist_limit,
        )

    # ------------------------------ Audit ------------------------------
    @app.get("/api/v1/audit/log")
    def get_audit_log():
        return list(audit_logger.iter_logs())

    @app.post("/api/v1/audit/undo/{hash_value}")
    def undo(hash_value: str):
        if undo_manager.undo(hash_value):
            return {"success": True}
        raise HTTPException(status_code=404, detail="Operation not found")

    return app
