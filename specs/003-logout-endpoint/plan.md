# Implementation Plan: Logout Endpoint

**Branch**: `hotfix/spec1-logout` | **Date**: 2026-03-02 | **Spec**: [./spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-logout-endpoint/spec.md`

## Summary

Add a stateless POST `/api/auth/logout` endpoint that terminates an authenticated user's session by confirming logout without maintaining any server-side state. Authenticated requests return 200 with a confirmation message; unauthenticated requests return 401. The client is responsible for discarding the token. This is a minimal, focused addition to existing JWT authentication infrastructure with zero impact on session management or token validation logic.

## Technical Context

**Language/Version**: Python 3.12.x  
**Primary Dependencies**: FastAPI, Pydantic, SQLAlchemy 2.0, pytest  
**Storage**: N/A (stateless endpoint, no persistence)  
**Testing**: pytest with FastAPI TestClient (integration tests only)  
**Target Platform**: Linux server runtime  
**Project Type**: Backend REST API (web-service)  
**Performance Goals**: Preserve current endpoint responsiveness; no material regression for auth path  
**Constraints**: Maintain layered architecture (API → Auth dependencies → JWT validation); keep existing error response conventions; no server-side session state  
**Scale/Scope**: Single endpoint addition affecting one auth service module

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Gate I — Python FastAPI Stack**: PASS. Endpoint uses FastAPI and existing JWT infrastructure; no stack changes.
- **Gate II — Layered Architecture Boundaries**: PASS (required design: route depends on `get_current_user` for auth validation).
- **Gate III — Validation & Centralized Error Handling**: PASS. Unauthenticated requests inherit 401 error handling from HTTPBearer dependency.
- **Gate IV — Security & Secret Hygiene**: PASS. No secrets involved; reuses existing JWT validation and auth pattern.
- **Gate V — Test Discipline & Quality Targets**: PASS. Integration tests required for two scenarios (auth/unauth); existing tests remain green.
- **Gate VI — SpecKit Workflow Discipline**: PASS. Specify completed; this document provides plan phase output before implementation.

Post-Design Re-check: PASS (no constitution violations introduced).

## Project Structure

### Documentation (this feature)

```text
specs/003-logout-endpoint/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── logout-api.md
└── checklists/
    └── requirements.md  # Specification quality checklist
```

### Source Code (repository root)

```text
app/
├── api/
│   ├── dependencies.py  # Existing: get_current_user (reused)
│   └── routes/
│       └── auth.py      # MODIFIED: Add logout endpoint
├── schemas/
│   └── auth.py          # MODIFIED: Add LogoutResponse schema (if needed)
├── services/
│   └── auth_service.py  # No changes (logout is stateless)
└── core/
    ├── errors.py        # Existing: APIError (reused)
    └── security.py      # Existing: decode_token (reused)

tests/
├── integration/
│   └── test_auth_endpoints.py  # MODIFIED: Add 2 new logout tests
└── unit/
    ├── test_auth_service.py     # No changes
    └── test_evaluation_service.py # No changes (regression baseline)
```

**Structure Decision**: Existing single FastAPI backend structure is retained; only relevant auth API route and integration test files are touched for minimal-risk hotfix scope. No new modules or services created. Logout is a simple route decorator addition that delegates verification to existing `get_current_user` dependency.

## Complexity Tracking

> No violations detected - all gates pass. No complexity justification needed.

---

## Technical Design Notes

### Endpoint Specification

**Route**: `POST /api/auth/logout`  
**Authentication**: Required (HTTPBearer token)  
**Parameters**: None (request body not needed)  
**Response (Success)**: HTTP 200 with `{ "message": "logged out" }`  
**Response (Unauthenticated)**: HTTP 401 Unauthorized (inherited from `get_current_user`)  
**State Changes**: None (stateless design - no database or cache updates)

### Implementation Approach

1. **Route Implementation**: Add new function decorated as `@router.post("/logout")` to `app/api/routes/auth.py`
2. **Dependency**: Use existing `get_current_user` from `app/api/dependencies.py` to enforce authentication
3. **Response**: Simple JSON response with success message (no state persistence)
4. **Error Handling**: Inherit 401 behavior from HTTPBearer when token is invalid/missing
5. **Tests**: Two integration tests: (1) authenticated logout returns 200, (2) unauthenticated logout returns 401

### Why This Design

- **Stateless**: No database writes, no token tracking, no session storage → aligns with MVP constraint
- **Minimal**: Single endpoint, reuses all existing auth machinery → low implementation risk
- **Consistent**: Follows existing FastAPI patterns (route decorator, HTTPBearer, APIError) → easy to understand
- **Non-Breaking**: Purely additive; no changes to register, login, or protected endpoints → zero regression risk

### Dependency Graph

```
POST /api/auth/logout
    ↓
@router.post("/logout")
    ↓
get_current_user (dependency)
    ↓
HTTPBearer (extracts + validates token)
    ↓
decode_token (JWT validation)
    ↓
Existing get_db + UserRepository (user verification)
    ↓
APIError(401) if any step fails
```

All components exist. No new services, no new repositories required.

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| Forgot to validate token | Low | High (auth bypass) | Use `get_current_user` dependency - impossible to miss |
| Broke existing auth | Low | High (regression) | Add integration tests for existing register/login flows |
| Changed error response format | Low | Medium (API contract) | Inherit error handling from HTTPBearer/APIError |

All risks are mitigation-by-design (reuse existing patterns).

---

## Assumptions

- JWT token is passed via `Authorization: Bearer <token>` header (existing convention).
- `get_current_user` dependency returns a User object if token is valid, raises APIError(401) otherwise.
- Logout is purely client-side token disposal (no server-side revocation needed for MVP).
- Response format `{ "message": "logged out" }` is acceptable (simple, testable).
- HTTP 401 is the appropriate response for unauthenticated requests (consistent with API convention).

## Prerequisites for Implementation

✅ Specification complete (spec.md, checklist)  
✅ No clarifications needed (analysis complete)  
✅ All gates passed (constitution check)  
✅ Existing auth infrastructure in place (HTTPBearer, get_current_user, APIError)  
✅ Test suite configured (pytest, TestClient)

**Status**: Ready for `/speckit.tasks` to generate task breakdown.
