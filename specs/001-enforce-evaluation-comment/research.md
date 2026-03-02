# Phase 0 Research: Evaluation Status Rule Enforcement

## Decision 1: Route status updates through evaluation service
- **Decision**: `PATCH /api/ideas/{id}/status` endpoint will delegate business-rule decisions to `app/services/evaluation_service.py`.
- **Rationale**: The existing bypass exists because route-level update path can avoid service rule checks. Centralizing in service establishes a single source of truth and aligns with layered architecture.
- **Alternatives considered**:
  - Re-implement comment checks in route layer (rejected: duplicated logic, drift risk).
  - Move checks to repository layer (rejected: repositories should not own business rules).

## Decision 2: Treat missing and blank comments as invalid for accepted/rejected
- **Decision**: For statuses `accepted` and `rejected`, both absent comment and whitespace-only comment are invalid and return HTTP 400.
- **Rationale**: Matches feature spec and existing service semantics (`strip()` then validate non-empty), ensuring consistent behavior across direct service calls and HTTP requests.
- **Alternatives considered**:
  - Permit blank comments but log warning (rejected: violates explicit business rule and acceptance criteria).
  - Auto-fill default comment (rejected: undermines audit quality and user intent).

## Decision 3: Preserve authorization guard at API boundary
- **Decision**: Keep admin-only dependency (`get_current_admin`) at route boundary and also keep service-level admin checks as defense in depth.
- **Rationale**: Maintains current security behavior and ensures non-admin requests fail with 403 before business logic mutation.
- **Alternatives considered**:
  - Remove route-level admin guard and rely only on service check (rejected: weaker boundary control and poorer API contract clarity).

## Decision 4: Add integration-first regression coverage
- **Decision**: Add/adjust endpoint integration tests for the four mandatory scenarios:
  1) under_review without comment -> 200
  2) accepted without comment -> 400
  3) rejected without comment -> 400
  4) non-admin status update -> 403
- **Rationale**: The bug is observed in real HTTP flow; integration tests are the most direct guardrail against recurrence.
- **Alternatives considered**:
  - Unit-only coverage in services (rejected: does not prove route wiring correctness).

## Decision 5: Keep out-of-scope modules untouched
- **Decision**: No functional changes for attachment upload/download flows.
- **Rationale**: Explicitly out-of-scope in the feature brief; minimizing surface area reduces hotfix risk.
- **Alternatives considered**:
  - Opportunistic cleanup in adjacent modules (rejected: scope creep).
