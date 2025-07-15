# Autonomy Planning Agent – Product Requirements Document (PRD)

> **Rev. 0.9 – July 15 2025**  
> Owner: Sharma Eye Care & Opticals (Product)  
> Status: Draft for Dev hand-off

---

## 0. Purpose & Scope

Create an **AI-augmented planning layer on top of GitHub** that delivers the speed and clarity of Linear while letting humans and agents share the same backlog. This PRD captures *all* requirements needed to ship the first market-ready release and to guide long-term evolution.

---

## 1. Problem Statement

*Builders still lose ≈6 h/week to backlog churn, duplicate issues, and context hunting—even after adopting AI code tools.* Existing trackers either add yet another UI (Jira) or stop at painless UX but no cognition (Linear). We need an agent that **keeps the backlog healthy, tells each actor their next best task, and learns local norms—without asking teams to leave GitHub or Slack/IDE.**

---

## 2. Vision 🛰️

> *“A planner that feels like Git, thinks like a senior TPM, and stays invisible until summoned.”*

- **Native** – works through GitHub issues, Tasklists, Projects v2.  
- **Flow-first** – surfaces tasks via CLI/IDE and Slack, not another web board.  
- **Trustable** – every bot edit is auditable, reversible, and explainable.  
- **Adaptive** – learns from reversals and fine-tunes behaviour per team.  
- **Open-core** – OSS foundations, SaaS convenience + enterprise security.

---

## 3. Success Metrics (v1 targets)

| KPI                                       | Target                  | How Measured         |
| ----------------------------------------- | ----------------------- | -------------------- |
| Mean time-to-next-task (`/autonomy next`) | ≤ 3 s (p95)             | CLI telemetry        |
| Grooming meeting time                     | -50 % within 2 sprints  | Self-reported survey |
| Bot-edit approval (thumbs-up)             | ≥ 85 %                  | Slack modal          |
| Weekly active slash-command users         | ≥ 70 % of pilot         | Analytics service    |
| Two paid conversions                      | within 60 days of pilot | Commercial ops       |

---

## 4. Personas

| Persona                      | Goals                                | Primary Surface          |
| ---------------------------- | ------------------------------------ | ------------------------ |
| **Developer (Power Hacker)** | Stay in flow, get next ticket fast   | VS Code / Cursor palette |
| **Product Manager**          | Backlog hygiene, progress visibility | Slack threads & digest   |
| **Designer**                 | Review tickets, minimal process      | Slack                    |
| **Founder/Exec**             | High-level progress, risks           | Daily digest             |

---

## 5. Core Hypotheses

1. **H1** – Builders adopt agent task-picking if it saves ≥ 30 min/week.  
2. **H2** – Transparent, reversible edits overcome trust objections.  
3. **H3** – Chat & IDE are the only mandatory surfaces; a web UI is optional.  
4. **H4** – Nightly backlog doctor reduces grooming effort by ≥ 50 %.

---

## 6. Licensing & Distribution Strategy

| Layer                                             | License                               | Rationale                                                      |
| ------------------------------------------------- | ------------------------------------- | -------------------------------------------------------------- |
| *Core Planning API, CLI, Slack Bot*               | GPLv3                                   | Fosters contributions, mirrors Git open-source ethos.          |
| *Agent Orchestration, LLM Prompts, Pattern Miner* | **Server Side Public License (SSPL)** | Open code, restricts SaaS copycats.                            |
| *Cloud SaaS*                                      | Proprietary                           | Adds value: autoscaling LLMs, analytics, audit streaming, SSO. |

*Follows Git (GPL2) + GitHub (proprietary SaaS) playbook.*

---

## 7. Functional Requirements

### 7.1 Task Retrieval & Update

- `/autonomy next [--me]` – returns highest-priority unblocked issue assigned to caller.  
- `/autonomy update <issue> --done --notes "…"` – closes issue, rolls over incomplete subtasks.

### 7.2 Issue Hierarchy Management

- Maintain **Epic → Feature → Task → Sub-task** using GitHub Tasklists.  
- Auto-create parent epics if missing; warn if orphan tasks > 3.

### 7.3 Backlog Doctor (Nightly Cron)

- Flag stale (> 14 days idle), duplicate (≥ 0.9 title/body sim.), or over-large (> 10 checklist items) issues.  
- Post digest to `#autonomy-daily` thread.

### 7.4 Reversibility & Undo

- All multi-issue edits land as PR on branch `autonomy/backlog-patch-<ts>`.  
- Comment embeds JSON diff hash.  
- **Undo** via `/autonomy undo <hash>` (CLI/Slack) within *N* commits window (configurable, default 5).  
- Undo reapplies inverse JSON patch to all touched artefacts.

### 7.5 Learning from Reversals

- Slack undo modal captures `reason`, `severity`, `flow_area`.  
- Pattern miner clusters reasons nightly; if same motif ≥ 3× → propose rule.

### 7.6 Security & Permissions

- MVP: PAT limited to `repo`, `issues:write`, `audit_log:read`.  
- Production: GitHub Audit Log Streaming → customer SIEM, SSO/SAML, SCIM, ip-allow-lists.

---

## 8. Non-Functional Requirements

| Aspect            | Requirement                                              |
| ----------------- | -------------------------------------------------------- |
| **Perf.**         | < 300 ms internal API latency, p95 CLI round-trip < 3 s  |
| **Scalability**   | 1 k issues/day, 50 repos/org @ MVP; horizontal workers   |
| **Reliability**   | 99.5 % uptime MVP → 99.9 % GA                            |
| **Compliance**    | SOC 2 Type I by GA; leverage GitHub audit for MVP        |
| **Observability** | Centralised logs, metrics, traces; per-tenant dashboards |

---

## 9. System Architecture (High-level)

```mermaid
flowchart LR
    subgraph Client Surfaces
        A1(Cursor/VS Code) -->|CLI REST| B(API)
        A2(Slack Bot) -->|HTTP| B
    end
    subgraph Core
        B(Planning-API) --> C{Task Router}
        C --> D[GitHub REST & GraphQL]
        C --> E[(Redis Task Queue)]
        E --> F[LLM Worker Pool]
        F --> G[(Postgres + pgvector)]
        C --> H[(Audit Log Writer)]
    end
