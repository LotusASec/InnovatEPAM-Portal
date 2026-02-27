# Implementation Plan: InnovatEPAM Portal MVP

**Branch**: `001-idea-management-mvp` | **Date**: 2026-02-27 | **Spec**: [specs/001-idea-management-mvp/spec.md](specs/001-idea-management-mvp/spec.md)
**Input**: Feature specification from `/specs/001-idea-management-mvp/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Deliver a one-day MVP for InnovatEPAM Portal with JWT authentication, idea submission
with optional attachments, idea listing and detail view with access control, and
admin-only evaluation workflow. The backend uses FastAPI, SQLAlchemy 2.0, and SQLite
with local file storage under ./storage/attachments and strict validation/error
handling per constitution and spec.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Pydantic, PyJWT, passlib[bcrypt]  
**Storage**: SQLite (MVP), local file storage in ./storage/attachments  
**Testing**: pytest, pytest-cov, FastAPI TestClient (Playwright optional)  
**Target Platform**: Linux server (local dev)  
**Project Type**: web-service API  
**Performance Goals**: <2s list response for up to 100 ideas; file download <5s for 5MB  
**Constraints**: one-day MVP, no notifications, logout returns success only  
**Scale/Scope**: single-tenant MVP, low traffic, limited concurrency

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- PASS: Python 3.11+, FastAPI, SQLAlchemy 2.0, SQLite for MVP
- PASS: Layered architecture (app/api, services, repositories, models, schemas)
- PASS: Pydantic validation and centralized error handling
- PASS: JWT auth, no secrets in repo
- PASS: Testing discipline (unit for services, integration for endpoints)

**Post-Design Check**: PASS (design and contracts align with constitution)

## Project Structure

### Documentation (this feature)

```text
specs/001-idea-management-mvp/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
app/
├── api/
│   ├── routes/
│   │   ├── auth.py
│   │   └── ideas.py
│   └── dependencies.py
├── services/
│   ├── auth_service.py
│   ├── idea_service.py
│   └── evaluation_service.py
├── repositories/
│   ├── user_repository.py
│   ├── idea_repository.py
│   ├── attachment_repository.py
│   └── evaluation_repository.py
├── models/
│   ├── base.py
│   ├── user.py
│   ├── idea.py
│   ├── attachment.py
│   └── evaluation_comment.py
├── schemas/
│   ├── auth.py
│   ├── ideas.py
│   └── evaluation.py
├── core/
│   ├── config.py
│   ├── security.py
│   └── errors.py
└── main.py

storage/
└── attachments/

tests/
├── unit/
│   ├── test_auth_service.py
│   ├── test_idea_service.py
│   └── test_validation.py
└── integration/
  ├── test_auth_endpoints.py
  ├── test_idea_endpoints.py
  └── test_evaluation_endpoints.py
```

**Structure Decision**: Single backend API with layered app/ structure and tests/
split into unit and integration per constitution.

## Complexity Tracking

No constitution violations.
