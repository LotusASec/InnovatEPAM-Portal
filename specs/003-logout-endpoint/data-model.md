# Phase 1 Data Model: Logout Endpoint

## Overview
This feature does not introduce new entities or data structures. It is a stateless endpoint that validates existing user identity (via JWT) and returns a confirmation message.

## No Persistent Entities
- **Logout**: Not an entity; it is a state transition confirmed to the client.
- **No state is persisted**: No database writes, no cache entries, no token records.

## Request/Response Models

### Logout Request
- **No body required**
- Authentication via HTTP Authorization header (Bearer token)

### Logout Response
- **Status**: 200 OK
- **Body**:
  ```json
  {
    "message": "logged out"
  }
  ```

## Error Responses

### 401 Unauthorized
- **Trigger**: Missing, expired, or invalid token in Authorization header
- **Body**:
  ```json
  {
    "error": "unauthorized"
  }
  ```
- **Behavior**: Inherited from existing `get_current_user` dependency

## Existing Entities Used

### User (existing)
- **Fields used in logout**: `id` (for authentication verification only; not returned in response)
- **Relationship**: User identity validated via JWT token, but no user records created/modified

### JWT Token (existing)
- **Purpose**: Client sends token in Authorization header; `get_current_user` validates signature and extracts user_id
- **Lifecycle**: Server never tracks token; client is responsible for discarding after logout
- **No modifications**: Logout does not write to database, does not invalidate token server-side

## State Diagram

```
Client (has token)
    ↓
POST /api/auth/logout
    ↓
Server validates token via get_current_user
    ↓
Token valid? → Yes → Return 200 { "message": "logged out" }
    ↓
Token invalid/missing? → Yes → Return 401 { "error": "unauthorized" }
    ↓
Client receives 200 → Client discards token locally
Client receives 401 → Client knows logout failed (already logged out?)
```

## No Backend State Changes
- No user table updates
- No logout table/log created
- No session store modified
- No token blacklist maintained
- No cache invalidation (no cache exists for tokens)

## Consistency with Existing System
- Logout response format mirrors other `{ "message": "..." }` responses in system
- Error responses follow APIError pattern (status code + error message)
- Authentication mechanism identical to protected endpoints (HTTPBearer + get_current_user)
