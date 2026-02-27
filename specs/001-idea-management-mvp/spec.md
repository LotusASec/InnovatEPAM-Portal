# Feature Specification: InnovatEPAM Portal MVP

**Feature Branch**: `001-idea-management-mvp`  
**Created**: 2026-02-27  
**Status**: Draft  
**Input**: InnovatEPAM Portal MVP (Python/FastAPI) with authentication, idea submission, listing, and evaluation workflow

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Registration (Priority: P1)

A new user can create an account by providing an email address and password. This is foundational to all other features.

**Why this priority**: P1 - Foundational. Without registration, users cannot access any other features.

**Independent Test**: User can register with valid credentials and log in immediately. This enables the entire application.

**Acceptance Scenarios**:

1. **Given** user is not logged in, **When** user submits registration with valid email and password, **Then** account is created and user receives success message
2. **Given** user is not logged in, **When** user submits registration with an email that already exists, **Then** user receives "email already registered" error and account is not created
3. **Given** user is not logged in, **When** user submits registration with invalid email format (e.g., "notanemail"), **Then** user receives "invalid email format" error
4. **Given** user is not logged in, **When** user submits registration with weak password (less than 8 characters), **Then** user receives "password must be at least 8 characters" error
5. **Given** user is not logged in, **When** user submits registration with all required fields, **Then** user can immediately log in with those credentials

---

### User Story 2 - User Login (Priority: P1)

A registered user can log in with their email and password to receive a JWT token for authenticated requests.

**Why this priority**: P1 - Foundational. Without login, users cannot submit ideas or access their data.

**Independent Test**: Registered user can login and receive a valid JWT token that grants access to protected endpoints.

**Acceptance Scenarios**:

1. **Given** user has registered, **When** user logs in with correct email and password, **Then** user receives a valid JWT token
2. **Given** user has registered, **When** user logs in with incorrect password, **Then** user receives "invalid credentials" error and no token is issued
3. **Given** user has registered, **When** user logs in with non-existent email, **Then** user receives "user not found" error and no token is issued
4. **Given** user has logged in, **When** user includes the JWT token in the Authorization header, **Then** protected endpoints are accessible
5. **Given** user is logged in, **When** user includes an invalid or expired JWT token, **Then** user receives "unauthorized" error

---

### User Story 3 - Idea Submission (Priority: P2)

An authenticated user can submit an idea with a title, description, category, and optional file attachment. The idea is initially in "submitted" status.

**Why this priority**: P2 - Core value. This is the primary user action that creates innovation proposals.

**Independent Test**: User can submit an idea with all required fields (with or without attachment) and it appears in their idea list with "submitted" status.

**Acceptance Scenarios**:

1. **Given** user is authenticated, **When** user submits idea with title, description, category, and PDF attachment (< 5MB), **Then** idea is created with "submitted" status and file is stored
2. **Given** user is authenticated, **When** user submits idea with title, description, and category (no attachment), **Then** idea is created with "submitted" status and no attachment field
3. **Given** user is authenticated, **When** user submits idea with empty title, **Then** user receives "title is required" error and idea is not created
4. **Given** user is authenticated, **When** user submits idea with empty description, **Then** user receives "description is required" error and idea is not created
5. **Given** user is authenticated, **When** user submits idea with empty category, **Then** user receives "category is required" error and idea is not created
6. **Given** user is authenticated, **When** user submits idea with attachment larger than 5MB, **Then** user receives "file size exceeds 5MB limit" error and idea is not created
7. **Given** user is authenticated, **When** user submits idea with attachment of type ".exe" (not allowed), **Then** user receives "file type not allowed" error and idea is not created
8. **Given** user is not authenticated, **When** user attempts to submit an idea, **Then** user receives "unauthorized" error
9. **Given** user is authenticated, **When** user submits idea with allowed attachment types (pdf, png, jpg, jpeg, txt), **Then** all are accepted without error

---

### User Story 4 - Idea Listing & View (Priority: P2)

Users can view a list of ideas they submitted. Admins can view all ideas. Users can view idea details including attachment download link.

**Why this priority**: P2 - Core value. Users need to see their submissions and track them through evaluation.

**Independent Test**: Submitter sees only own ideas; admin sees all ideas. Idea details page shows all metadata and allows attachment download.

**Acceptance Scenarios**:

1. **Given** authenticated non-admin user has submitted 3 ideas, **When** user requests their idea list, **Then** user sees all 3 own ideas only (no other users' ideas)
2. **Given** admin user is authenticated, **When** admin requests all ideas, **Then** admin sees all ideas from all users
3. **Given** non-admin user has submitted 0 ideas, **When** user requests their idea list, **Then** user sees empty list with message "you have not submitted any ideas"
4. **Given** user views an idea detail page, **When** an attachment exists, **Then** user sees attachment filename and download link
5. **Given** user views an idea detail page with no attachment, **When** checking for attachment section, **Then** no attachment section is displayed
6. **Given** user clicks download link on an idea with attachment, **When** request is successful, **Then** file is downloaded to user's device
7. **Given** user is not authenticated, **When** user attempts to access idea list, **Then** user receives "unauthorized" error

---

### User Story 5 - Evaluation Workflow (Priority: P3)

Admin users can change an idea's status (submitted, under_review, accepted, rejected) and add comments when accepting or rejecting.

**Why this priority**: P3 - Important for MVP but can be done manually initially; completes the workflow.

**Independent Test**: Admin can change idea status and add comment; status change is recorded and visible to submitter.

**Acceptance Scenarios**:

1. **Given** admin is viewing an idea with status "submitted", **When** admin changes status to "under_review", **Then** status is updated and submitter receives notification
2. **Given** admin is evaluating an idea, **When** admin accepts the idea with a comment, **Then** status changes to "accepted", comment is stored, and submitter is notified
3. **Given** admin is evaluating an idea, **When** admin rejects the idea with a comment, **Then** status changes to "rejected", comment is stored, and submitter is notified
4. **Given** admin tries to change status without adding a comment when accepting/rejecting, **When** admin submits without comment, **Then** user receives "comment is required for acceptance or rejection" error
5. **Given** non-admin user is viewing an idea, **When** non-admin attempts to change status, **Then** user receives "permission denied" error
6. **Given** admin changes status of an idea, **When** submitter views their idea, **Then** submitter sees the updated status and comment

---

### User Story 6 - User Logout (Priority: P3)

User can logout to invalidate their session (client-side JWT discard is sufficient for MVP).

**Why this priority**: P3 - Nice-to-have for MVP. JWT tokens will expire by default; client can discard token locally.

**Independent Test**: User can call logout endpoint; after logout, old token should be treated as invalid by the system.

**Acceptance Scenarios**:

1. **Given** user is authenticated with a valid JWT token, **When** user logs out, **Then** logout endpoint returns success message
2. **Given** user has logged out, **When** user attempts to use their previous JWT token, **Then** token is rejected with "unauthorized" error
3. **Given** user is not authenticated, **When** user calls logout endpoint, **Then** user receives "unauthorized" error

---

### Edge Cases

- What happens when a user tries to register while already logged in? (Allow or redirect to dashboard)
- What happens when file upload fails mid-transfer? (Cleanup partial upload, return error)
- What happens if admin rejects idea but accidental click? (Allow status change back if needed or add confirmation)
- What happens when attachment is deleted from disk but idea record still references it? (Show "attachment unavailable" not 500 error)
- What happens when user submits two ideas simultaneously? (Both should be created, no race condition)

## Requirements *(mandatory)*

### Functional Requirements

**Authentication & Authorization**:

- **FR-001**: System MUST accept user registration with email and password
- **FR-002**: System MUST validate email format on registration
- **FR-003**: System MUST enforce minimum password length of 8 characters on registration
- **FR-004**: System MUST prevent duplicate email registration
- **FR-005**: System MUST issue JWT token on successful login with correct credentials
- **FR-006**: System MUST reject login requests with invalid email or password
- **FR-007**: System MUST validate JWT token on all protected endpoints and reject invalid/expired tokens
- **FR-008**: System MUST support logout endpoint that invalidates JWT tokens
- **FR-009**: System MUST return "unauthorized" (401) for requests missing JWT token on protected endpoints
- **FR-010**: System MUST return "permission denied" (403) when non-admin users attempt admin-only actions

**Idea Submission**:

- **FR-011**: System MUST allow authenticated users to submit ideas with title, description, and category
- **FR-012**: System MUST accept optional file attachments (one per idea) with max size 5MB
- **FR-013**: System MUST enforce allowed file types: pdf, png, jpg, jpeg, txt
- **FR-014**: System MUST reject attachments exceeding 5MB with clear error message
- **FR-015**: System MUST reject files with disallowed extensions with clear error message
- **FR-016**: System MUST validate that title, description, and category are not empty
- **FR-017**: System MUST store submitted ideas with initial status of "submitted"
- **FR-018**: System MUST store file attachments locally in the file system
- **FR-019**: System MUST associate each idea with the submitting user
- **FR-020**: System MUST return "unauthorized" (401) when non-authenticated users attempt to submit ideas

**Idea Listing & View**:

- **FR-021**: System MUST allow users to retrieve list of their own submitted ideas only (non-admin)
- **FR-022**: System MUST allow admin users to retrieve list of all ideas from all users
- **FR-023**: System MUST return empty list when user has no submitted ideas
- **FR-024**: System MUST display idea details including title, description, category, status, and submitter info
- **FR-025**: System MUST display attachment filename and provide download link when attachment exists
- **FR-026**: System MUST handle missing attachments gracefully (show "attachment unavailable" not error)
- **FR-027**: System MUST allow users to download attachments they submitted
- **FR-028**: System MUST return "unauthorized" (401) when non-authenticated users attempt to view ideas

**Evaluation Workflow**:

- **FR-029**: System MUST allow admin users to change idea status to: submitted, under_review, accepted, rejected
- **FR-030**: System MUST require comment when accepting or rejecting an idea
- **FR-031**: System MUST reject status change to accepted/rejected without providing a comment
- **FR-032**: System MUST store comment text associated with status changes
- **FR-033**: System MUST prevent non-admin users from changing idea status
- **FR-034**: System MUST return "permission denied" (403) when non-admin attempts status change

**Error Handling**:

- **FR-035**: System MUST return JSON error responses with consistent structure: `{error: "message"}`
- **FR-036**: System MUST return appropriate HTTP status codes: 400 (bad request), 401 (unauthorized), 403 (forbidden), 409 (conflict), 422 (validation error), 500 (server error)
- **FR-037**: System MUST not expose internal stack traces or sensitive information in error messages

### Key Entities

- **User**: Represents a registered user. Attributes: id (unique identifier), email (unique), password_hash (hashed), created_at, is_admin (boolean flag)
- **Idea**: Represents a submitted innovation idea. Attributes: id, title, description, category, status (enum: submitted/under_review/accepted/rejected), submitter_id (foreign key to User), created_at, updated_at
- **Attachment**: Represents a file attachment to an idea. Attributes: id, idea_id (foreign key), filename, file_path (local storage path), file_size, upload_timestamp
- **EvaluationComment**: Represents admin comments on idea evaluation. Attributes: id, idea_id (foreign key), admin_id (foreign key to User), comment_text, status_change_to, created_at

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete registration flow in under 1 minute (from initial form to success confirmation)
- **SC-002**: Users can complete login and receive JWT token in under 10 seconds
- **SC-003**: Users can submit an idea (with or without attachment) in under 2 minutes
- **SC-004**: Idea listing page loads in under 2 seconds for up to 100 ideas
- **SC-005**: Attachment download completes in under 5 seconds for typical 5MB file
- **SC-006**: Admin can change idea status and add comment in under 30 seconds per idea
- **SC-007**: System correctly validates and rejects all invalid inputs (wrong email format, weak passwords, oversized files, disallowed file types)
- **SC-008**: All authentication checks work correctly: JWT validation prevents unauthorized access to protected endpoints
- **SC-009**: Permission checks work correctly: non-admin users cannot access admin features; users see only their own ideas
- **SC-010**: All API responses use consistent JSON error format with descriptive messages
- **SC-011**: System achieves at least 95% successful request completion rate on happy path scenarios
- **SC-012**: File attachments are correctly stored and retrievable without corruption
