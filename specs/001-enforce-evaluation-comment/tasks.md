---
description: "Task list for Evaluation Status Rule Enforcement"
---

# Tasks: Evaluation Status Rule Enforcement

**Input**: Design documents from `/specs/001-enforce-evaluation-comment/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/status-update-api.md, quickstart.md

**Context**: Hotfix to close business rule bypass where HTTP status updates can skip comment validation for accepted/rejected decisions.

**Organization**: Tasks are grouped by user story to enable focused implementation and independent testing.

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This project uses a single backend structure:
- API routes: `app/api/routes/`
- Services: `app/services/`
- Integration tests: `tests/integration/`
- Unit tests: `tests/unit/`

---

## Phase 1: User Story 1 - Enforce Comment Rule on Decision Statuses (Priority: P1) 🎯 MVP

**Goal**: Admin updating idea to accepted/rejected must provide a non-blank comment, while under_review does not require comment. This closes the business rule bypass in HTTP requests.

**Independent Test**: Admin can submit status update to `under_review` without comment successfully (200), while `accepted` and `rejected` updates without comment are rejected with 400 error.

### Implementation for User Story 1

- [x] T001 [US1] Update status endpoint in app/api/routes/ideas.py to route through evaluation_service.update_status instead of idea_service.update_idea_status
- [x] T002 [US1] Pass both status and comment from StatusUpdate schema to evaluation_service.update_status in app/api/routes/ideas.py
- [x] T003 [P] [US1] Add integration test for under_review without comment success in tests/integration/test_evaluation_endpoints.py
- [x] T004 [P] [US1] Add integration test for accepted without comment failure in tests/integration/test_evaluation_endpoints.py
- [x] T005 [P] [US1] Add integration test for rejected without comment failure in tests/integration/test_evaluation_endpoints.py

**Checkpoint**: At this point, accepted/rejected status updates without comment should fail with 400, while under_review should succeed.

---

## Phase 2: User Story 2 - Keep Authorization Guardrails Intact (Priority: P2)

**Goal**: Non-admin users must remain unable to update idea statuses, ensuring security boundaries don't regress while fixing validation behavior.

**Independent Test**: A non-admin attempting to change idea status receives a 403 permission denied response.

### Implementation for User Story 2

- [x] T006 [US2] Add integration test for non-admin status update forbidden in tests/integration/test_evaluation_endpoints.py

**Checkpoint**: Non-admin users should receive 403 when attempting any status update.

---

## Phase 3: User Story 3 - Single Source of Truth for Status Rules (Priority: P3)

**Goal**: Status validation and rule enforcement centralized in evaluation service so API behavior and service behavior cannot diverge.

**Independent Test**: Integration tests and service-level tests both assert the same accepted/rejected comment requirement and produce aligned outcomes.

### Implementation for User Story 3

- [x] T007 [US3] Run existing unit tests in tests/unit/test_evaluation_service.py to verify service rules remain consistent
- [x] T008 [US3] Run all integration tests to verify no conflicting rule behavior between service and API layers

**Checkpoint**: All evaluation tests pass without conflicts, proving single source of truth architecture.

---

## Phase 4: Polish & Validation

**Purpose**: Ensure no regressions and validate complete solution

- [x] T009 Run full test suite with pytest to verify no regressions
- [x] T010 Validate quickstart.md scenarios manually if needed
- [x] T011 Verify out-of-scope endpoints (logout, attachments) remain unchanged

---

## Dependencies & Execution Order

### Phase Dependencies

- **User Story 1 (Phase 1)**: Can start immediately - core fix
- **User Story 2 (Phase 2)**: Can start after US1 T001-T002 complete (depends on route changes)
- **User Story 3 (Phase 3)**: Can start after US1 and US2 complete (validation phase)
- **Polish (Phase 4)**: Depends on all user stories complete

### Within Each User Story

- **US1**: T001-T002 must complete before integration tests T003-T005 (route must be updated first)
- **US1 Tests**: T003, T004, T005 are parallel once route is ready
- **US2**: T006 can be written independently
- **US3**: T007 and T008 are validation tasks

### Parallel Opportunities

- Once T001-T002 complete, all integration tests (T003, T004, T005, T006) can be written in parallel
- T007 and T008 can run in parallel during validation phase

---

## Parallel Example: User Story 1 Integration Tests

```bash
# After route is updated (T001-T002), launch all integration tests together:
Task: "Add integration test for under_review without comment success in tests/integration/test_evaluation_endpoints.py"
Task: "Add integration test for accepted without comment failure in tests/integration/test_evaluation_endpoints.py"
Task: "Add integration test for rejected without comment failure in tests/integration/test_evaluation_endpoints.py"
```

---

## Implementation Strategy

### Hotfix Approach (Minimal Risk)

1. **Core Fix (US1 T001-T002)**: Update route to delegate to evaluation_service
2. **Validation Coverage (US1 T003-T005)**: Add integration tests for comment enforcement
3. **Security Verification (US2 T006)**: Confirm non-admin 403 still works
4. **Alignment Check (US3 T007-T008)**: Verify service and API rules match
5. **Regression Guard (Polish)**: Run full test suite

### MVP First (User Story 1 Only)

1. Complete T001-T002 (route changes)
2. Complete T003-T005 (integration tests)
3. **STOP and VALIDATE**: Verify accepted/rejected without comment returns 400
4. Run existing tests to check for regressions
5. If stable, proceed to US2 and US3

### Expected Test Outcomes

Based on contracts/status-update-api.md:

| Scenario | Status | Comment | Expected | Error Message |
|----------|--------|---------|----------|---------------|
| Admin → under_review | under_review | None | 200 OK | - |
| Admin → accepted | accepted | None | 400 Bad Request | "comment is required for acceptance or rejection" |
| Admin → rejected | rejected | "   " (blank) | 400 Bad Request | "comment is required for acceptance or rejection" |
| Non-admin → any | under_review | None | 403 Forbidden | "permission denied" |

---

## Technical Notes

### Files Modified

- `app/api/routes/ideas.py`: Update `update_idea_status_endpoint` to call `evaluation_service.update_status(db, user, idea_id, status_update.status, status_update.comment)`
- `tests/integration/test_evaluation_endpoints.py`: Add 4 new integration test functions

### Files NOT Modified (Out of Scope)

- `app/api/routes/auth.py`: Logout behavior unchanged
- `app/api/routes/ideas.py`: Attachment upload/download unchanged
- `app/services/idea_service.py`: update_idea_status function preserved but not called by status endpoint
- `app/services/evaluation_service.py`: Already has correct validation logic

### Existing Service Logic

The `app/services/evaluation_service.py` already implements the correct rules:
- `update_status(db, admin_user, idea_id, new_status, comment)` signature exists
- Validates admin permission (403 if not admin)
- Validates status in VALID_STATUSES (400 if invalid)
- Validates comment required for accepted/rejected (400 if missing/blank)
- Persists status change and evaluation comment

The fix is purely about routing HTTP requests through this service instead of bypassing it.

---

## Verification Checklist

After completing all tasks:

- [ ] `pytest tests/integration/test_evaluation_endpoints.py -v` passes all new tests
- [ ] `pytest tests/unit/test_evaluation_service.py -v` passes all existing service tests
- [ ] `pytest` runs full suite without regressions
- [ ] Admin can update status to under_review without comment (200)
- [ ] Admin cannot update status to accepted without comment (400)
- [ ] Admin cannot update status to rejected without comment (400)
- [ ] Non-admin cannot update any status (403)
- [ ] Out-of-scope endpoints work unchanged (logout, attachments)

---

## Notes

- This is a focused hotfix - minimize scope and risk
- Evaluation service already has correct logic - just need to route through it
- All four integration test scenarios are mandatory per FR-008
- Test fail messages should match error messages in contracts/status-update-api.md
- Preserve existing behavior for valid status updates (FR-007)
- No schema migrations needed (data-model.md confirms no new entities)
