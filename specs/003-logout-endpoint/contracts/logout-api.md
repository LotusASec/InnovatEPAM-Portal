# Contract: Logout API

## Endpoint
- `POST /api/auth/logout`

## Authentication & Authorization
- Requires Bearer JWT token in `Authorization` header
- No role-based authorization; authenticated users (any role) can logout

## Request

### Headers
```
Authorization: Bearer <jwt-token>
```

### Body
- No request body required

## Response Success (200 OK)

```json
{
  "message": "logged out"
}
```

**Behavior**: Authentication was successful. Server confirms logout. Client should discard the token locally.

## Response Error (403 Forbidden)

```json
{
  "error": "forbidden"
}
```

**Trigger**:
- Missing Authorization header

**Behavior**: FastAPI HTTPBearer returns 403 when Authorization header is absent. Client must include valid Bearer token to proceed.

## Response Error (401 Unauthorized)

```json
{
  "error": "unauthorized"
}
```

**Trigger**: One or more of:
- Malformed token (not prefixed with "Bearer ")
- Empty token value
- Invalid token signature
- Expired token
- Token claims missing required fields (e.g., `sub` user ID)
- User referenced in token does not exist in database

**Behavior**: Client must not discard token based on logout acceptance; token remains valid until expiration or (if client implements) local removal.

## Edge Cases

### Case A: Logout with valid token
- **Request**:
```
POST /api/auth/logout
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
- **Response**: `200 OK` with `{ "message": "logged out" }`
- **Guarantee**: Logout confirmed; client should discard token.

### Case B: Logout with missing Authorization header
- **Request**:
```
POST /api/auth/logout
(no Authorization header)
```
- **Response**: `403 Forbidden` with `{ "error": "forbidden" }`
- **Guarantee**: FastAPI HTTPBearer returns 403. Request rejected; no logout performed.

### Case C: Logout with invalid/expired token
- **Request**:
```
POST /api/auth/logout
Authorization: Bearer invalid-or-expired-token
```
- **Response**: `401 Unauthorized` with `{ "error": "unauthorized" }`
- **Guarantee**: Request rejected; no logout performed.

### Case D: Multiple logouts (same token)
- **First logout**: `200 OK`
- **Second logout with same token**: `200 OK` (token still valid on server; no server-side tracking prevents re-logout)
- **Note**: Client is responsible for preventing redundant logouts by not reusing a discarded token.

### Case E: Logout after token expiration
- **Request**: Token has expired
- **Response**: `401 Unauthorized`
- **Note**: Server rejects expired tokens automatically; no special logout behavior.

## Invariants

1. **Stateless operation**: Server does not create logs, blacklists, or session records for logout.
2. **No database side effects**: No rows inserted, updated, or deleted.
3. **Consistent error handling**: Response codes and format match existing auth endpoints.
4. **Client-side responsibility**: Server confirms logout but does not enforce token discard; client owns token lifecycle.

## Server Behavior

- **Never blocks previous tokens**: Logout confirmation does not revoke the token server-side.
- **Token validation unchanged**: Subsequent requests with same token are evaluated per normal JWT rules (signature, expiration).
- **No audit logs**: MVP omits server-side logout logging (can be added post-MVP if audit trail required).
