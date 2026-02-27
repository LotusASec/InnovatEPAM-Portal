<!--
Sync Impact Report
- Version change: [CONSTITUTION_VERSION] -> 1.0.0
- Modified principles: Template placeholders -> InnovatEPAM Portal MVP principles
- Added sections: Technology and Architecture Standards; Development Workflow and Quality Gates
- Removed sections: None
- Templates requiring updates:
	- ✅ .specify/templates/plan-template.md (no change needed)
	- ✅ .specify/templates/spec-template.md (no change needed)
	- ✅ .specify/templates/tasks-template.md (no change needed)
	- ✅ .specify/templates/checklist-template.md (no change needed)
- Follow-up TODOs:
	- TODO(RATIFICATION_DATE): original adoption date not provided
-->
# InnovatEPAM Portal MVP Constitution

## Core Principles

### I. Python FastAPI Stack (NON-NEGOTIABLE)
All backend development MUST use Python 3.11+ with FastAPI. Persistence MUST use
SQLAlchemy 2.0 and SQLite for the MVP (swap later only via a constitution
amendment). Authentication MUST use JWT.
Rationale: a single, consistent stack keeps velocity high and integration risk low.

### II. Layered Architecture Boundaries
Code MUST follow the layered structure: app/api (routers), app/services (business
logic), app/repositories (db access), app/models (SQLAlchemy models), app/schemas
(Pydantic). Cross-layer access is forbidden (e.g., routers must not hit the DB
directly). Business rules live only in services.
Rationale: clear boundaries prevent coupling and improve testability.

### III. Validation and Centralized Error Handling
All request inputs MUST be validated with Pydantic schemas. Errors MUST be handled
via centralized FastAPI exception handlers with consistent error payloads. Raw
tracebacks or unhandled exceptions must never leak to clients.
Rationale: predictable input and error handling improves reliability and security.

### IV. Security and Secret Hygiene
Secrets MUST NOT be committed to the repo. Use environment variables or a secret
manager, and avoid logging sensitive data (tokens, credentials, PII). JWT tokens
MUST be validated on protected routes.
Rationale: reduces breach risk and accidental exposure.

### V. Test Discipline and Quality Targets
Core service logic MUST follow TDD (tests written first, failing, then implement).
Unit tests MUST cover services and utilities. Integration tests MUST cover FastAPI
endpoints using TestClient. Assertions MUST be exact (True/False, exact strings),
never tautological, and include boundary tests for validation. E2E tests MAY be
added using Playwright (Python) for 1-2 critical journeys only. Mutation testing
target is 75% using mutmut when time permits.
Rationale: strict tests protect behavior and reduce regressions.

## Technology and Architecture Standards

- Python 3.11+ with FastAPI is the only approved web stack for the MVP.
- SQLite is required for the MVP; any change requires a constitution amendment.
- SQLAlchemy 2.0 is the required ORM; raw SQL usage needs explicit justification.
- Centralized error handling is mandatory for all API routes.
- No secrets are stored in the repository or committed to version control.

## Development Workflow and Quality Gates

- All features must comply with the layered architecture and validation rules.
- TDD applies to core business logic in app/services.
- Integration tests using FastAPI TestClient are required for new endpoints.
- Boundary validations must be tested explicitly.
- When time permits, run mutation tests and aim for 75% mutmut score.

**Required Commands**:

- Create venv: python -m venv .venv
- Install: pip install -r requirements.txt
- Run app: uvicorn app.main:app --reload
- Run tests: pytest -q
- Coverage: pytest --cov=app --cov-report=term-missing
- (Optional) Mutation: mutmut run

## Governance

- The constitution supersedes all other practices and templates.
- Amendments require a documented rationale, updated version, and review.
- Versioning follows semantic versioning: MAJOR for breaking governance changes,
	MINOR for new or materially expanded guidance, PATCH for clarifications.
- All PRs MUST include a constitution compliance check when touching architecture,
	testing discipline, or stack decisions.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): original adoption date not provided | **Last Amended**: 2026-02-27
