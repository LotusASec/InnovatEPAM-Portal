---

description: "Task list for InnovatEPAM Portal MVP implementation"
---

# Tasks: InnovatEPAM Portal MVP

**Input**: Design documents from `/specs/001-idea-management-mvp/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Tests are included and required by constitution (TDD for services, integration for endpoints).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Each task includes file paths and a validation command

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create directories and init packages in app/ and tests/ plus storage/attachments (app/__init__.py, app/api/__init__.py, app/services/__init__.py, app/repositories/__init__.py, app/models/__init__.py, app/schemas/__init__.py, app/core/__init__.py); Validate: `ls app/api app/services app/repositories app/models app/schemas app/core tests/unit tests/integration storage/attachments`
- [x] T002 Create requirements.txt with FastAPI, SQLAlchemy 2.0, PyJWT, passlib[bcrypt], python-multipart, uvicorn, pytest, pytest-cov; Validate: `pip install -r requirements.txt`
- [x] T003 Add pytest.ini with testpaths and markers in pytest.ini; Validate: `pytest -q --collect-only`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T004 Implement settings in app/core/config.py (JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRES_MINUTES, DATABASE_URL, STORAGE_DIR); Validate: `python -c "from app.core.config import settings; print(settings.jwt_algorithm)"`
- [x] T005 Implement DB engine and session in app/core/database.py and declarative base in app/models/base.py; Validate: `python -c "from app.core.database import engine"`
- [x] T006 Define User model in app/models/user.py with email uniqueness and is_admin; Validate: `python -c "from app.models.user import User"`
- [x] T007 Define Idea model in app/models/idea.py with status enum and relationships; Validate: `python -c "from app.models.idea import Idea"`
- [x] T008 Define Attachment model in app/models/attachment.py with one-to-one relationship to Idea; Validate: `python -c "from app.models.attachment import Attachment"`
- [x] T009 Define EvaluationComment model in app/models/evaluation_comment.py with admin relationship; Validate: `python -c "from app.models.evaluation_comment import EvaluationComment"`
- [x] T010 Implement security helpers in app/core/security.py (hash_password, verify_password, create_access_token, decode_token); Validate: `python -c "from app.core.security import create_access_token"`
- [x] T011 Implement API error types and handlers in app/core/errors.py and wire into app/main.py; Validate: `python -c "from app.core.errors import APIError"`
- [x] T012 Create FastAPI app in app/main.py with startup to create tables (SQLAlchemy create_all); Validate: `python -c "from app.main import app; print(app.title)"`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - User Registration (Priority: P1) 🎯 MVP

**Goal**: Allow new users to register with email and password

**Independent Test**: User can register successfully and receives expected response or error

### Tests for User Story 1

- [x] T013 [US1] Add register unit tests to tests/unit/test_auth_service.py (valid registration, duplicate email, invalid email, weak password); Validate: `pytest -q tests/unit/test_auth_service.py::test_register_success`
- [x] T014 [US1] Add register integration tests in tests/integration/test_auth_endpoints.py; Validate: `pytest -q tests/integration/test_auth_endpoints.py::test_register_success`

### Implementation for User Story 1

- [x] T015 [US1] Define register schemas in app/schemas/auth.py (RegisterRequest, RegisterResponse); Validate: `python -c "from app.schemas.auth import RegisterRequest"`
- [x] T016 [US1] Implement user repository in app/repositories/user_repository.py (get_by_email, create_user); Validate: `python -c "from app.repositories.user_repository import UserRepository"`
- [x] T017 [US1] Implement register service in app/services/auth_service.py with password hashing and duplicate checks; Validate: `pytest -q tests/unit/test_auth_service.py::test_register_success`
- [x] T018 [US1] Implement POST /auth/register in app/api/routes/auth.py and include router in app/main.py; Validate: `pytest -q tests/integration/test_auth_endpoints.py::test_register_success`

---

## Phase 4: User Story 2 - User Login (Priority: P1)

**Goal**: Allow registered users to log in and receive JWT access tokens

**Independent Test**: User can log in and access protected endpoints with JWT

### Tests for User Story 2

- [x] T019 [US2] Add login unit tests to tests/unit/test_auth_service.py (success, invalid password, user not found); Validate: `pytest -q tests/unit/test_auth_service.py::test_login_success`
- [x] T020 [US2] Add login integration tests in tests/integration/test_auth_endpoints.py; Validate: `pytest -q tests/integration/test_auth_endpoints.py::test_login_success`

### Implementation for User Story 2

- [x] T021 [US2] Define login schemas in app/schemas/auth.py (LoginRequest, TokenResponse); Validate: `python -c "from app.schemas.auth import LoginRequest"`
- [x] T022 [US2] Implement login service in app/services/auth_service.py and JWT issuance; Validate: `pytest -q tests/unit/test_auth_service.py::test_login_success`
- [x] T023 [US2] Add auth dependencies in app/api/dependencies.py (get_current_user, get_current_admin) using JWT; Validate: `python -c "from app.api.dependencies import get_current_user"`
- [x] T024 [US2] Implement POST /auth/login in app/api/routes/auth.py; Validate: `pytest -q tests/integration/test_auth_endpoints.py::test_login_success`

---

## Phase 5: User Story 3 - Idea Submission + Listing/Detail (Priority: P2)

**Goal**: Authenticated users can create ideas and view their own ideas without attachments

**Independent Test**: User can create idea and see it in list and detail view

### Tests for User Story 3

- [x] T025 [US3] Add idea service unit tests in tests/unit/test_idea_service.py (create, list, get with ownership); Validate: `pytest -q tests/unit/test_idea_service.py::test_create_idea_success`
- [x] T026 [US3] Add idea integration tests in tests/integration/test_idea_endpoints.py (create, list, detail); Validate: `pytest -q tests/integration/test_idea_endpoints.py::test_create_idea_success`

### Implementation for User Story 3

- [x] T027 [US3] Define idea schemas in app/schemas/ideas.py (IdeaCreate, IdeaSummary, IdeaDetail); Validate: `python -c "from app.schemas.ideas import IdeaCreate"`
- [x] T028 [US3] Implement idea repository in app/repositories/idea_repository.py (create, list_by_user, list_all, get_by_id); Validate: `python -c "from app.repositories.idea_repository import IdeaRepository"`
- [x] T029 [US3] Implement idea service in app/services/idea_service.py with validation and ownership checks; Validate: `pytest -q tests/unit/test_idea_service.py::test_create_idea_success`
- [x] T030 [US3] Implement routes in app/api/routes/ideas.py for POST /ideas, GET /ideas, GET /ideas/{id} and include router in app/main.py; Validate: `pytest -q tests/integration/test_idea_endpoints.py::test_create_idea_success`

---

## Phase 6: User Story 4 - Attachments Download + Validation (Priority: P2)

**Goal**: Allow optional file attachments on idea submission with validation and download

**Independent Test**: User can upload allowed attachment, reject disallowed/oversized files, and download stored attachments

### Tests for User Story 4

- [ ] T031 [US4] Add attachment validation unit tests in tests/unit/test_validation.py (size and type checks); Validate: `pytest -q tests/unit/test_validation.py::test_rejects_large_file`
- [ ] T032 [US4] Add attachment integration tests in tests/integration/test_idea_endpoints.py (upload and download); Validate: `pytest -q tests/integration/test_idea_endpoints.py::test_upload_attachment_success`

### Implementation for User Story 4

- [ ] T033 [US4] Implement attachment repository in app/repositories/attachment_repository.py; Validate: `python -c "from app.repositories.attachment_repository import AttachmentRepository"`
- [ ] T034 [US4] Extend schemas in app/schemas/ideas.py with AttachmentInfo and attachment fields; Validate: `python -c "from app.schemas.ideas import AttachmentInfo"`
- [ ] T035 [US4] Implement file validation and storage in app/services/idea_service.py using STORAGE_DIR and update create flow; Validate: `pytest -q tests/unit/test_validation.py::test_rejects_large_file`
- [ ] T036 [US4] Update POST /ideas to accept multipart and add GET /ideas/{id}/attachment in app/api/routes/ideas.py; Validate: `pytest -q tests/integration/test_idea_endpoints.py::test_upload_attachment_success`

---

## Phase 7: User Story 5 - Evaluation Workflow (Priority: P3)

**Goal**: Admin can update idea status with required comment for accept/reject

**Independent Test**: Admin can change status and comment is enforced and visible

### Tests for User Story 5

- [ ] T037 [US5] Add evaluation unit tests in tests/unit/test_evaluation_service.py (status transitions, comment required); Validate: `pytest -q tests/unit/test_evaluation_service.py::test_accept_requires_comment`
- [ ] T038 [US5] Add evaluation integration tests in tests/integration/test_evaluation_endpoints.py; Validate: `pytest -q tests/integration/test_evaluation_endpoints.py::test_admin_can_update_status`

### Implementation for User Story 5

- [ ] T039 [US5] Define evaluation schemas in app/schemas/evaluation.py (StatusUpdateRequest, StatusUpdateResponse); Validate: `python -c "from app.schemas.evaluation import StatusUpdateRequest"`
- [ ] T040 [US5] Implement evaluation repository in app/repositories/evaluation_repository.py; Validate: `python -c "from app.repositories.evaluation_repository import EvaluationRepository"`
- [ ] T041 [US5] Implement evaluation service in app/services/evaluation_service.py (no notifications, return updated status); Validate: `pytest -q tests/unit/test_evaluation_service.py::test_accept_requires_comment`
- [ ] T042 [US5] Implement PATCH /ideas/{id}/status in app/api/routes/ideas.py (admin only) and return updated status; Validate: `pytest -q tests/integration/test_evaluation_endpoints.py::test_admin_can_update_status`

---

## Phase 8: User Story 6 - Logout (Priority: P3)

**Goal**: Provide logout endpoint that returns success and requires authentication

**Independent Test**: Logout returns success for authenticated users and 401 otherwise

### Tests for User Story 6

- [ ] T043 [US6] Add logout integration tests in tests/integration/test_auth_endpoints.py; Validate: `pytest -q tests/integration/test_auth_endpoints.py::test_logout_success`

### Implementation for User Story 6

- [ ] T044 [US6] Implement POST /auth/logout in app/api/routes/auth.py (success response only); Validate: `pytest -q tests/integration/test_auth_endpoints.py::test_logout_success`

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and project hygiene

- [ ] T045 Run full unit test suite and fix failures in tests/unit/; Validate: `pytest -q tests/unit`
- [ ] T046 Run full integration test suite and fix failures in tests/integration/; Validate: `pytest -q tests/integration`
- [ ] T047 Validate quickstart commands from specs/001-idea-management-mvp/quickstart.md; Validate: `python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt && pytest -q`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: Depend on Foundational phase completion
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (Registration)**: Depends on Foundational
- **US2 (Login)**: Depends on US1 and Foundational
- **US3 (Ideas without attachments)**: Depends on US2 and Foundational
- **US4 (Attachments)**: Depends on US3
- **US5 (Evaluation)**: Depends on US3 and US2
- **US6 (Logout)**: Depends on US2

### Within Each User Story

- Tests MUST be written and fail before implementation (TDD for services)
- Schemas/models before repositories, repositories before services, services before routes
- Integration tests before endpoint implementation

### Parallel Opportunities

- Phase 1 tasks can be parallelized if different files are touched
- Test tasks and schema/repository tasks can be parallelized if they are on different files

---

## Parallel Example: User Story 3

```bash
Task: "T025 Add idea service unit tests in tests/unit/test_idea_service.py"
Task: "T027 Define idea schemas in app/schemas/ideas.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (Registration)
4. Validate US1 tests and proceed to US2

### Incremental Delivery

1. Setup + Foundational
2. US1 + US2 (Auth)
3. US3 (Ideas without attachments)
4. US4 (Attachments upload/download + validation)
5. US5 (Evaluation)
6. US6 (Logout)
7. Polish

### Parallel Team Strategy

If multiple developers are available, proceed with schema/repository tasks and test tasks in parallel per phase to reduce cycle time.
