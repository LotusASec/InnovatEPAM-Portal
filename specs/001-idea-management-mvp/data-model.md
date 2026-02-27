# Data Model: InnovatEPAM Portal MVP

## Overview

Entities: User, Idea, Attachment, EvaluationComment.
Relationships: User 1..* Idea; Idea 0..1 Attachment; Idea 0..* EvaluationComment; User (admin) 1..* EvaluationComment.

## User

- id: integer, primary key
- email: string, unique, required
- password_hash: string, required
- is_admin: boolean, default false
- created_at: datetime, required

Constraints:
- Email must be unique and valid format.
- Password stored as hash only.

## Idea

- id: integer, primary key
- title: string, required
- description: text, required
- category: string, required
- status: enum (submitted, under_review, accepted, rejected), default submitted
- submitter_id: integer, foreign key to User.id
- created_at: datetime, required
- updated_at: datetime, required

Constraints:
- title, description, category cannot be empty.
- status transitions:
  - submitted -> under_review | accepted | rejected
  - under_review -> accepted | rejected
  - accepted -> accepted (no change)
  - rejected -> rejected (no change)

## Attachment

- id: integer, primary key
- idea_id: integer, foreign key to Idea.id, unique (one attachment per idea)
- original_filename: string, required
- stored_filename: string, required
- file_path: string, required
- content_type: string, required
- file_size: integer, required
- created_at: datetime, required

Constraints:
- file_size <= 5MB
- allowed extensions: pdf, png, jpg, jpeg, txt

## EvaluationComment

- id: integer, primary key
- idea_id: integer, foreign key to Idea.id
- admin_id: integer, foreign key to User.id
- comment_text: text, required
- status_change_to: enum (accepted, rejected), required
- created_at: datetime, required

Constraints:
- comment_text required when status_change_to is accepted or rejected.

