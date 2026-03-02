# Implementation Plan: Evaluation Status Rule Enforcement

**Branch**: `001-enforce-evaluation-comment` | **Date**: 2026-03-02 | **Spec**: [/specs/001-enforce-evaluation-comment/spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-enforce-evaluation-comment/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Close the status-update rule bypass by routing the HTTP `PATCH /api/ideas/{id}/status` flow through the evaluation service so final decision statuses (`accepted`, `rejected`) always enforce non-blank comments, while preserving existing role-based authorization and non-regression for valid status updates.

## Technical Context

**Language/Version**: Python 3.12.x  
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Pydantic, pytest, pytest-cov  
**Storage**: SQLite (MVP)  
**Testing**: pytest (unit + integration with FastAPI TestClient)  
**Target Platform**: Linux server runtime
**Project Type**: Backend web-service (REST API)  
**Performance Goals**: Preserve current endpoint responsiveness; no material regression for status update path  
**Constraints**: Maintain layered architecture (API → Service → Repo), keep existing error response conventions, keep out-of-scope features unchanged  
**Scale/Scope**: Narrow hotfix scope affecting one endpoint flow and related tests

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Gate I — Python FastAPI Stack**: PASS. Changes stay in existing Python/FastAPI stack.
- **Gate II — Layered Architecture Boundaries**: PASS (required design: route delegates business rule to service).
- **Gate III — Validation & Centralized Error Handling**: PASS. Validation errors remain controlled and consistent.
- **Gate IV — Security & Secret Hygiene**: PASS. No secret handling changes; auth/role checks preserved.
- **Gate V — Test Discipline & Quality Targets**: PASS. Integration tests expanded for required scenarios; existing tests remain green.
- **Gate VI — SpecKit Workflow Discipline**: PASS. Specify completed; this document provides plan phase output before implementation.

Post-Design Re-check: PASS (no constitution violations introduced).

## Project Structure

### Documentation (this feature)

```text
specs/001-enforce-evaluation-comment/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── status-update-api.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
app/
├── api/
│   ├── dependencies.py
│   └── routes/
│       └── ideas.py
├── services/
│   ├── idea_service.py
│   └── evaluation_service.py
├── core/
│   └── errors.py
└── models/
    ├── idea.py
    └── evaluation_comment.py

tests/
├── integration/
│   └── test_evaluation_endpoints.py
└── unit/
    └── test_evaluation_service.py
```

**Structure Decision**: Existing single FastAPI backend structure is retained; only relevant API, service, and integration/unit test files are touched for minimal-risk hotfix scope.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
