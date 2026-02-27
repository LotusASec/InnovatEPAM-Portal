# Research: InnovatEPAM Portal MVP

## Decision 1: JWT authentication approach

- Decision: Use access tokens only (no refresh tokens) with HS256, claims: sub, iat, exp. Token lifetime 30 minutes.
- Rationale: One day MVP, simplest secure flow. Logout is client-side discard only.
- Alternatives considered:
  - Access + refresh tokens: better long-lived sessions but more implementation time.
  - Session cookies: simpler but deviates from JWT requirement.

## Decision 2: Password hashing

- Decision: Use passlib with bcrypt for password hashing.
- Rationale: Widely used, secure, simple for MVP.
- Alternatives considered:
  - Argon2: strong but adds extra dependency complexity.
  - SHA-256: rejected due to insufficient security.

## Decision 3: File uploads and storage

- Decision: Validate file extension and MIME type; enforce max 5MB; store under ./storage/attachments/ with UUID filename and preserve original filename in DB.
- Rationale: Simple, aligns with local storage MVP requirement and prevents unsafe file types.
- Alternatives considered:
  - Cloud storage (S3): more scalable but out of scope for 1 day.
  - DB blob storage: larger DB size and slower retrieval.

## Decision 4: SQLAlchemy 2.0 with SQLite

- Decision: Use SQLAlchemy 2.0 declarative models, session-per-request, SQLite file database for MVP.
- Rationale: Required by constitution and MVP constraints.
- Alternatives considered:
  - PostgreSQL: more robust but not required for MVP.
  - SQLModel: higher-level but not required by constitution.

## Decision 5: Testing strategy

- Decision: Unit tests for services and auth helpers; integration tests for each endpoint with FastAPI TestClient; strict exact assertions.
- Rationale: Aligns with constitution and MVP scope.
- Alternatives considered:
  - End-to-end UI tests: deferred; only 1-2 critical journeys if time permits.
  - Full mutation testing: optional (mutmut) due to time constraints.

