Autonomy Planning Agent – Product Requirements Document (PRD)
=============================================================

> **Rev. 0.9 – July 15 2025**Owner: Mehul Bhardwaj 
(Product)Status: Draft for Dev hand‑off

0\. Purpose & Scope
-------------------

Create an **AI‑augmented planning layer on top of GitHub** that delivers the speed and clarity of Linear while letting humans and agents share the same backlog. This PRD captures _all_ requirements needed to ship the first market‑ready release and to guide long‑term evolution.

1\. Problem Statement
---------------------

_Builders still lose ≈6 h/week to backlog churn, duplicate issues, and context hunting—even after adopting AI code tools._Existing trackers either add yet another UI (Jira) or stop at painless UX but no cognition (Linear). We need an agent that **keeps the backlog healthy, tells each actor their next best task, and learns local norms—without asking teams to leave GitHub or Slack/IDE.**

2\. Vision 🛰️
--------------

> _“A planner that feels like Git, thinks like a senior TPM, and stays invisible until summoned.”_

*   **Native** – works through GitHub issues, Tasklists, Projects v2.
    
*   **Flow‑first** – surfaces tasks via CLI/IDE and Slack, not another web board.
    
*   **Trustable** – every bot edit is auditable, reversible, and explainable.
    
*   **Adaptive** – learns from reversals and fine‑tunes behaviour per team.
    
*   **Open‑core** – OSS foundations, SaaS convenience + enterprise security.
    

3\. Success Metrics (v1 targets)
--------------------------------

KPITargetHow Measured Mean time‑to‑next‑task (/autonomy next)≤ 3 s (p95)CLI telemetryGrooming meeting time‑50 % within 2 sprintsSelf‑reported surveyBot‑edit approval (thumbs‑up)≥ 85 %Slack modalWeekly active slash‑command users≥ 70 % of pilotAnalytics serviceTwo paid conversionswithin 60 days of pilotCommercial ops

4\. Personas
------------

PersonaGoalsPrimary Surface**Developer (Power Hacker)**Stay in flow, get next ticket fastVS Code / Cursor palette**Product Manager**Backlog hygiene, progress visibilitySlack threads & digest**Designer**Review tickets, minimal processSlack**Founder/Exec**High‑level progress, risksDaily digest

5\. Core Hypotheses
-------------------

1.  **H1** – Builders adopt agent task‑picking if it saves ≥ 30 min/week.
    
2.  **H2** – Transparent, reversible edits overcome trust objections.
    
3.  **H3** – Chat & IDE are the only mandatory surfaces; a web UI is optional.
    
4.  **H4** – Nightly backlog doctor reduces grooming effort by ≥ 50 %.
    

6\. Licensing & Distribution Strategy
-------------------------------------

LayerLicenseRationale_Core Planning API, CLI, Slack Bot_MITFosters contributions, mirrors Git open‑source ethos._Agent Orchestration, LLM Prompts, Pattern Miner_**Server Side Public License (SSPL)**Open code, restricts SaaS copycats._Cloud SaaS_ProprietaryAdds value: autoscaling LLMs, analytics, audit streaming, SSO.

_Follows Git (GPL2) + GitHub (proprietary SaaS) playbook._

7\. Functional Requirements
---------------------------

### 7.1 Task Retrieval & Update

*   **/autonomy next \[--me\]** – returns highest‑priority unblocked issue assigned to caller.
    
*   **/autonomy update \--done --notes "…"** – closes issue, rolls over incomplete subtasks.
    

### 7.2 Issue Hierarchy Management

*   Maintain **Epic → Feature → Task → Sub‑task** using GitHub Tasklists.
    
*   Auto‑create parent epics if missing; warn if orphan tasks > 3.
    

### 7.3 Backlog Doctor (Nightly Cron)

*   Flag stale (> 14 days idle), duplicate (≥ 0.9 title/body sim.), or over‑large (> 10 checklist items) issues.
    
*   Post digest to #autonomy‑daily thread.
    

### 7.4 Reversibility & Undo

*   All multi‑issue edits land as PR on branch autonomy/backlog‑patch‑.
    
*   Comment embeds JSON diff hash.
    
*   **Undo** via /autonomy undo  (CLI/Slack) within _N_ commits window (configurable, default 5).
    
*   Undo reapplies inverse JSON patch to all touched artefacts.
    

### 7.5 Learning from Reversals

*   Slack undo modal captures reason, severity, flow\_area.
    
*   Pattern miner clusters reasons nightly; if same motif ≥ 3× -> propose rule.
    

### 7.6 Security & Permissions

*   MVP: PAT limited to repo, issues:write, audit\_log:read.
    
*   Production: GitHub Audit Log Streaming → customer SIEM, SSO/SAML, SCIM, ip‑allow‑lists.
    

8\. Non‑Functional Requirements
-------------------------------

AspectRequirement**Perf.**< 300 ms internal API latency, p95 CLI round‑trip < 3 s**Scalability**1 k issues/day, 50 repos/org @ MVP; horizontal workers**Reliability**99.5 % uptime MVP → 99.9 % GA**Compliance**SOC 2 Type I by GA; leverage GitHub audit for MVP**Observability**Centralised logs, metrics, traces; per‑tenant dashboards

9\. System Architecture (High‑level)
------------------------------------

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   flowchart LR      subgraph Client Surfaces          A1(Cursor/VS Code) -->|CLI REST| B(API)          A2(Slack Bot) -->|HTTP| B      end      subgraph Core          B(Planning‑API) --> C{Task Router}          C --> D[GitHub REST & GraphQL]          C --> E[(Redis Task Queue)]          E --> F[LLM Worker Pool]          F --> G[(Postgres + pgvector)]          C --> H[(Audit Log Writer)]      end   `

10\. Data Model (simplified)
----------------------------

EntityFieldsNotes**IssueRecord**gh\_issue\_id, epic\_id, state, labels\[\], assignee, priority, typeCached mirror from GitHub**RevisionLog**hash, timestamp, actor, diff\_jsonFor undo & audit**ReversalFeedback**hash, reason, severity, flow\_areaTraining signal**Rule**pattern\_embedding, answer, confidenceLearned heuristics

11\. MVP Deliverables & Timeline
--------------------------------

WeekDeliverable0–1Repo bootstrap, PAT secret vault, basic CLI skeleton2–3next & update endpoints, Slack slash‑command4Issue hierarchy sync using Tasklists beta5Nightly backlog doctor + Slack digest6Shadow‑branch PR & undo command, analytics events

Pilot with 10 squads starts end‑Week 6.

12\. Roadmap (Post‑MVP)
-----------------------

1.  **Learning Reversals** – pattern miner, adaptive rules.
    
2.  **Enterprise Hardening** – SSO, audit streaming, secret scanning gates.
    
3.  **Contextual RAG** – embed code/docs/PRs for NL Q&A.
    
4.  **Velocity Forecast AI** – scope‑cut suggestions, risk heat‑maps.
    
5.  **Plugin SDK** – custom priority scorers, alt LLMs.
    
6.  **Non‑dev Stakeholders** – marketing/op intake templates, ambiguity resolver.
    

13\. Open Source vs Cloud Components
------------------------------------

ComponentOSSCloud‑onlyPlanning API core✔ CLI & Slack bot✔ LLM prompts & orchestrationSSPLSaaS tuning & cachingAnalytics dashboard–✔Audit streaming, SSO, RBAC UI–✔

14\. Testing & QA
-----------------

*   Unit tests for every API handler, 90 % cover.
    
*   Integration tests against GitHub API sandbox.
    
*   Load test: 1 k next calls/min.
    
*   Security: static scan (CodeQL), secret scan, dependency audit.
    

15\. Risks & Mitigations
------------------------

RiskMitigationLow trust in auto editsShadow‑branch + undo, diff commentsGitHub Tasklists API instabilityAdapter layer; fallback to plain checklistsLLM latency/costBatch calls, streaming, model selectorOSS copycats eating SaaSSSPL for orchestration, fast cloud cadenceEnterprise compliancePhase‑3 SOC 2, audit streaming

16\. Glossary
-------------

*   **Tasklist** – GitHub beta feature turning checklist items into child issues.
    
*   **Backlog Doctor** – nightly job cleaning & flagging backlog health.
    
*   **Shadow‑branch** – temporary branch holding backlog edits for review.
    
*   **Undo Hash** – content‑addressed ID of a bot change.
