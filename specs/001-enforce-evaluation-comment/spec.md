# Feature Specification: Evaluation Status Rule Enforcement

**Feature Branch**: `001-enforce-evaluation-comment`  
**Created**: 2026-03-02  
**Status**: Draft  
**Input**: User description: "Enforce evaluation status-comment rule in HTTP API by routing status updates through evaluation service so accepted/rejected without comment returns 400, non-admin remains 403, and add integration coverage for under_review without comment plus accepted/rejected missing comment failures."

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Enforce Comment Rule on Decision Statuses (Priority: P1)

An admin updating an idea to a final decision status must provide a meaningful comment so evaluation outcomes are auditable and consistent.

**Why this priority**: This closes a business rule bypass in real HTTP requests and prevents invalid accepted/rejected decisions from being stored.

**Independent Test**: Admin can submit a status update to `under_review` without comment successfully, while `accepted` and `rejected` updates without comment are rejected with a 400 error.

**Acceptance Scenarios**:

1. **Given** an authenticated admin and an existing idea, **When** admin sets status to `under_review` with no comment, **Then** request succeeds with 200 and status is updated.
2. **Given** an authenticated admin and an existing idea, **When** admin sets status to `accepted` with missing or blank comment, **Then** request fails with 400 and clear validation message.
3. **Given** an authenticated admin and an existing idea, **When** admin sets status to `rejected` with missing or blank comment, **Then** request fails with 400 and clear validation message.

---

### User Story 2 - Keep Authorization Guardrails Intact (Priority: P2)

Non-admin users must remain unable to update idea statuses, even after routing all updates through the evaluation service.

**Why this priority**: Security and role boundaries must not regress while fixing validation behavior.

**Independent Test**: A non-admin attempting to change idea status receives a 403 permission denied response.

**Acceptance Scenarios**:

1. **Given** an authenticated non-admin user and an existing idea, **When** user sends a status update request, **Then** request fails with 403 permission denied.

---

### User Story 3 - Single Source of Truth for Status Rules (Priority: P3)

Status validation and rule enforcement should be centralized so API behavior and service behavior cannot diverge.

**Why this priority**: Improves maintainability and prevents future rule drift between HTTP layer and domain logic.

**Independent Test**: Integration tests and service-level tests both assert the same accepted/rejected comment requirement and produce aligned outcomes.

**Acceptance Scenarios**:

1. **Given** the status update API, **When** any status update request is processed, **Then** business rule decisions are delegated to the evaluation service.
2. **Given** existing evaluation tests, **When** new endpoint tests are run, **Then** all continue to pass without conflicting rule behavior.

---

### Edge Cases

- Missing comment field in payload for `accepted` and `rejected` must be treated as invalid.
- Comment field containing only whitespace must be treated as missing.
- Unknown status values must still return a validation error and must not persist state changes.
- Requests for non-existent idea IDs must return a not-found response without side effects.
- Out-of-scope endpoints (logout, attachment upload/download) must remain behaviorally unchanged.

## Assumptions

- Existing role model (admin vs non-admin) and permission semantics are retained.
- Existing status set remains unchanged (`submitted`, `under_review`, `accepted`, `rejected`).
- Error response format remains consistent with current API conventions.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST process all idea status update requests through the evaluation service business logic.
- **FR-002**: System MUST allow admins to set status to `under_review` without requiring a comment.
- **FR-003**: System MUST reject status updates to `accepted` when comment is missing or blank.
- **FR-004**: System MUST reject status updates to `rejected` when comment is missing or blank.
- **FR-005**: System MUST return HTTP 400 with a clear, user-facing error message when `accepted`/`rejected` comment validation fails.
- **FR-006**: System MUST continue returning HTTP 403 for non-admin attempts to update status.
- **FR-007**: System MUST preserve existing behavior for valid admin status updates and persist successful changes.
- **FR-008**: System MUST include integration test coverage for: under_review without comment success, accepted without comment failure, rejected without comment failure, and non-admin forbidden update.
- **FR-009**: System MUST keep logout and attachment upload/download behavior unchanged as out-of-scope.

### Key Entities *(include if feature involves data)*

- **Idea**: A submitted proposal whose evaluation status can be updated by authorized users.
- **Evaluation Update Request**: A status change intent containing target status and optional comment.
- **Evaluation Comment**: Reviewer-provided rationale required for final decisions (`accepted`/`rejected`).
- **User Role**: Access classification distinguishing admin users from non-admin users for authorization.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of admin requests to set status `accepted` or `rejected` without a non-blank comment are rejected with HTTP 400 in integration tests.
- **SC-002**: 100% of admin requests to set status `under_review` without comment succeed with HTTP 200 in integration tests.
- **SC-003**: 100% of non-admin status update attempts are rejected with HTTP 403 in integration tests.
- **SC-004**: Existing evaluation-related unit and integration tests remain passing with no regressions after the change.
- **SC-005**: No scope creep: logout and attachment upload/download test behavior remains unchanged before and after this feature.
