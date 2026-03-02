# Phase 0 Research: Logout Endpoint

## Decision 1: Stateless logout without token blacklist
- **Decision**: Logout endpoint returns 200 confirmation but maintains no server-side state (no blacklist, no revocation list).
- **Rationale**: MVP constraint explicitly forbids token blacklist/revocation. Client discards token locally. Aligns with FastAPI stateless design principle and JWT philosophy: token validity determined only by signature and expiration.
- **Alternatives considered**:
  - Token blacklist implementation (rejected: out of scope for MVP, requires persistent storage or cache layer).
  - Session storage (rejected: out of scope, violates stateless API principle).

## Decision 2: Reuse get_current_user dependency for authentication
- **Decision**: Logout endpoint requires authentication by depending on `get_current_user` from existing HTTPBearer pattern.
- **Rationale**: Eliminates code duplication, ensures consistent auth behavior across all protected routes. HTTPBearer automatically raises 401 for missing/invalid tokens.
- **Alternatives considered**:
  - Custom auth check in logout route (rejected: duplicates existing logic, maintenance burden).
  - Optional auth on logout (rejected: violates security boundary - logout requires authenticated user).

## Decision 3: Simple JSON response format
- **Decision**: Logout returns `{ "message": "logged out" }` response.
- **Rationale**: Matches MVP simplicity principle. No complex structure, user_id, timestamp, or additional metadata needed. Tests are deterministic and easy to validate.
- **Alternatives considered**:
  - Return timestamp or additional metadata (rejected: scope creep, not in spec).
  - Redirect instead of JSON (rejected: REST API convention requires JSON response).

## Decision 4: Inherit error handling from HTTPBearer
- **Decision**: 401 Unauthorized response for missing/invalid token is automatic from HTTPBearer + get_current_user dependency.
- **Rationale**: No custom error handling needed. Consistent with all other protected endpoints in the system. Eliminates risk of inconsistent responses.
- **Alternatives considered**:
  - Custom 401 handler in logout route (rejected: unnecessary, existing pattern sufficient).

## Decision 5: Integration tests only (no unit tests)
- **Decision**: Add two integration tests (authenticated logout, unauthenticated logout) without separate unit tests.
- **Rationale**: Endpoint is a thin wrapper around existing `get_current_user`. No business logic to unit test. Integration tests verify the complete auth flow + logout response. Matches pattern used in existing auth_endpoints tests.
- **Alternatives considered**:
  - Add unit tests for logout service (rejected: no service created, endpoint is route-only).

## Decision 6: No schema generation for response
- **Decision**: Return response as plain dict from route; Pydantic will auto-serialize to JSON.
- **Rationale**: Minimal. Response structure is simple and won't be reused. Avoids schema boilerplate. Matches response pattern in existing endpoints.
- **Alternatives considered**:
  - Create LogoutResponse Pydantic model (rejected: overkill for single `message` field).
