# Feature Specification: Authentication Logout Endpoint

**Feature Branch**: `hotfix/spec1-logout`  
**Created**: 2026-03-02  
**Status**: Draft  
**Input**: User description: "Add POST /api/auth/logout endpoint. If request is authenticated (valid token), return 200 with a simple message. Logout must not break existing auth flows."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Authenticated User Logout (Priority: P1) 🎯 MVP

An authenticated user can terminate their session by calling the logout endpoint, which returns a success message without maintaining session state on the server.

**Why this priority**: This is the core logout capability required by Spec1. Users need a way to explicitly logout after logging in, and the endpoint must be functional and discoverable.

**Independent Test**: An authenticated user with a valid JWT token can POST to `/api/auth/logout` and receive a 200 response with a logout confirmation message.

**Acceptance Scenarios**:

1. **Given** an authenticated user with a valid JWT token, **When** user POSTs to `/api/auth/logout` with the Authorization header, **Then** server responds with HTTP 200 and a JSON message (e.g., `{ "message": "logged out" }`).
2. **Given** an authenticated user after successful logout, **When** the client discards the token, **Then** subsequent requests without the token are rejected as unauthorized (existing behavior preserved).

---

### User Story 2 - Unauthenticated Logout Rejection (Priority: P2)

Prevent logout attempts from users who are not authenticated, maintaining consistent security boundaries.

**Why this priority**: Security guardrail to ensure logout endpoint honors auth requirements. Prevents confusion and maintains predictable API behavior.

**Independent Test**: A request without valid authentication receives an error response (403 for missing header, 401 for invalid/expired token).

**Acceptance Scenarios**:

1. **Given** an unauthenticated user with missing Authorization header, **When** user POSTs to `/api/auth/logout`, **Then** server responds with HTTP 403 Forbidden (FastAPI HTTPBearer default).
2. **Given** a user with invalid or expired token, **When** user POSTs to `/api/auth/logout`, **Then** server responds with HTTP 401 Unauthorized.

---

### User Story 3 - Non-Regression of Existing Auth Flows (Priority: P3)

Ensure that the new logout endpoint does not disrupt existing authentication workflows (register, login, protected endpoints).

**Why this priority**: Confirms that logout addition does not introduce regressions. Validates compatibility with existing system.

**Independent Test**: All existing auth and protected endpoint tests continue to pass after logout implementation.

**Acceptance Scenarios**:

1. **Given** existing register and login functionality, **When** those endpoints are called, **Then** they continue to work as before.
2. **Given** protected endpoints (ideas, evaluation), **When** called with valid token, **Then** access is granted as before.

---

### Edge Cases

- Logout with missing Authorization header must return 403 Forbidden (FastAPI HTTPBearer library default behavior).
- Logout with malformed or expired token must return 401 Unauthorized.
- Multiple logout calls from the same user session must be handled consistently (logout again with same valid token returns 200; logout with invalid/expired token returns 401).
- Logout endpoint must not create any server-side state or database entries (stateless design).

## Assumptions

- JWT is the authentication method (as used in existing auth system).
- No session storage or token blacklist will be implemented (MVP scope).
- Client is responsible for discarding the token after receiving logout confirmation.
- Logout response format will be simple JSON message without complex structure.
- FastAPI HTTPBearer returns 403 when Authorization header is missing; 401 when token is invalid or expired.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expose a POST endpoint at `/api/auth/logout` that requires authentication (valid JWT token in Authorization header).
- **FR-002**: System MUST return HTTP 200 with a JSON message when an authenticated user logs out (e.g., `{ "message": "logged out" }`).
- **FR-003**: System MUST return HTTP 403 Forbidden when logout is requested without an Authorization header (HTTPBearer default).
- **FR-004**: System MUST return HTTP 401 Unauthorized when logout is requested with an invalid or expired token.
- **FR-005**: System MUST NOT create or store any server-side session state, token blacklist, or logout records (stateless design).
- **FR-006**: System MUST preserve all existing authentication flows (register, login) and protected endpoint access after logout implementation.
- **FR-007**: System MUST document that logout is a client-side operation: the server confirms logout, but the client is responsible for discarding the token.
- **FR-008**: System MUST include integration tests verifying: authenticated logout returns 200, missing header returns 403, invalid token returns 401, and existing auth flows remain unaffected.

### Key Entities *(include if feature involves data)*

- **User Session (Client-side)**: The client's in-memory or local storage token. Logout documentation must clarify that the server does not track sessions; client must remove token locally.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: New logout endpoint integration tests pass: authenticated logout returns 200, missing header returns 403, invalid/expired token returns 401.
- **SC-002**: Full test suite (all existing unit and integration tests) remains passing with zero regressions after logout implementation.
- **SC-003**: Logout endpoint documentation clearly explains: HTTPBearer returns 403 for missing Authorization header; invalid/expired tokens return 401; stateless design ensures server confirms logout but does not track sessions.
- **SC-004**: Logout endpoint is callable from an authenticated session and returns within expected API response time (no server-side storage overhead).
