# Phase 1 Data Model: Evaluation Status Rule Enforcement

## Overview
This feature does not introduce new persistent entities. It constrains and aligns behavior of existing status update flow.

## Entities

### 1. Evaluation Update Request (existing API payload)
- **Fields**:
  - `status` (string enum): `submitted | under_review | accepted | rejected`
  - `comment` (optional string)
- **Validation Rules**:
  - `status` must be one of allowed statuses.
  - For `accepted` and `rejected`, `comment` must be present and non-blank after trimming.
  - For `under_review` and `submitted`, `comment` may be omitted.

### 2. Idea (existing domain entity)
- **Fields used in this feature**:
  - `id`
  - `status`
  - `submitter_id`
- **State Transition Concern**:
  - Endpoint updates `Idea.status` only through service logic.

### 3. EvaluationComment (existing domain entity)
- **Fields used in this feature**:
  - `idea_id`
  - `admin_id`
  - `comment_text`
  - `status_change_to`
- **Validation Rules**:
  - Persisted when comment is provided/required by status.

### 4. User Role Context (existing auth model)
- **Fields used in this feature**:
  - `id`
  - `is_admin`
- **Authorization Rule**:
  - Non-admin update attempt must fail with 403.

## State Transitions

### Allowed Statuses
- `submitted`
- `under_review`
- `accepted`
- `rejected`

### Rule Constraints
- Transition to `accepted` requires non-blank comment.
- Transition to `rejected` requires non-blank comment.
- Transition to `under_review` does not require comment.
- Invalid status must fail without persistence.

## Error Model
- `400`: comment requirement violation for accepted/rejected or invalid status.
- `403`: non-admin update attempt.
- `404`: idea not found.

## Persistence Impact
- No schema migration required.
- Existing tables and fields are reused.
