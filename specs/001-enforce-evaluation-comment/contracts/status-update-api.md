# Contract: Status Update API Rule Enforcement

## Endpoint
- `PATCH /api/ideas/{idea_id}/status`

## Authentication & Authorization
- Requires Bearer JWT.
- Admin role required.

## Request Body
```json
{
  "status": "under_review | accepted | rejected | submitted",
  "comment": "optional string"
}
```

## Behavioral Contract

### Case A: Admin sets `under_review` without comment
- **Request**:
```json
{"status":"under_review"}
```
- **Response**: `200 OK`
- **Guarantee**: status is updated.

### Case B: Admin sets `accepted` without comment
- **Request**:
```json
{"status":"accepted"}
```
- **Response**: `400 Bad Request`
- **Error payload**:
```json
{"error":"comment is required for acceptance or rejection"}
```

### Case C: Admin sets `rejected` with blank comment
- **Request**:
```json
{"status":"rejected", "comment":"   "}
```
- **Response**: `400 Bad Request`
- **Error payload**:
```json
{"error":"comment is required for acceptance or rejection"}
```

### Case D: Non-admin attempts status update
- **Request**:
```json
{"status":"under_review"}
```
- **Response**: `403 Forbidden`
- **Error payload**:
```json
{"error":"permission denied"}
```

## Invariants
- Status update business rules are enforced by evaluation service as single source of truth.
- Out-of-scope behaviors remain unchanged (logout, attachment upload/download).
