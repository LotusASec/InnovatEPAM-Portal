# HTTP API Contracts: InnovatEPAM Portal MVP

Base URL: /api
Auth: Bearer JWT in Authorization header: "Authorization: Bearer <token>"
Error format: {"error": "message"}

## POST /auth/register

Request JSON:
- email: string
- password: string

Success 201:
- {"id": 1, "email": "user@example.com"}

Errors:
- 400 {"error": "invalid email format"}
- 400 {"error": "password must be at least 8 characters"}
- 409 {"error": "email already registered"}

## POST /auth/login

Request JSON:
- email: string
- password: string

Success 200:
- {"access_token": "<jwt>", "token_type": "bearer"}

Errors:
- 401 {"error": "invalid credentials"}
- 404 {"error": "user not found"}

## POST /auth/logout

Request: Authorization header required

Success 200:
- {"success": true}

Errors:
- 401 {"error": "unauthorized"}

## POST /ideas

Request: multipart/form-data
- title: string (required)
- description: string (required)
- category: string (required)
- file: file (optional)

Success 201:
- {"id": 10, "title": "...", "description": "...", "category": "...", "status": "submitted", "attachment": {"id": 5, "filename": "proposal.pdf"}}

Errors:
- 400 {"error": "title is required"}
- 400 {"error": "description is required"}
- 400 {"error": "category is required"}
- 400 {"error": "file size exceeds 5MB limit"}
- 400 {"error": "file type not allowed"}
- 401 {"error": "unauthorized"}

## GET /ideas

Success 200:
- [{"id": 10, "title": "...", "status": "submitted", "category": "...", "created_at": "..."}]

Errors:
- 401 {"error": "unauthorized"}

## GET /ideas/{id}

Success 200:
- {
  "id": 10,
  "title": "...",
  "description": "...",
  "category": "...",
  "status": "submitted",
  "created_at": "...",
  "updated_at": "...",
  "submitter": {"id": 1, "email": "user@example.com"},
  "attachment": {"id": 5, "filename": "proposal.pdf"},
  "evaluation": {"status_change_to": "accepted", "comment_text": "...", "admin_id": 2}
}

Errors:
- 401 {"error": "unauthorized"}
- 403 {"error": "permission denied"}
- 404 {"error": "idea not found"}

## GET /ideas/{id}/attachment

Success 200:
- File download (binary)

Errors:
- 401 {"error": "unauthorized"}
- 403 {"error": "permission denied"}
- 404 {"error": "attachment unavailable"}

## PATCH /ideas/{id}/status

Request JSON:
- status: "submitted" | "under_review" | "accepted" | "rejected"
- comment: string (required for accepted or rejected)

Success 200:
- {"id": 10, "status": "under_review", "comment": null}

Errors:
- 400 {"error": "comment is required for acceptance or rejection"}
- 401 {"error": "unauthorized"}
- 403 {"error": "permission denied"}
- 404 {"error": "idea not found"}

