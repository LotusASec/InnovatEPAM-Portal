---
description: "Task list for EPAM UI Theme & Typography implementation"
---

# Tasks: EPAM UI Theme & Typography

**Input**: Design documents from `/specs/002-epam-ui-theme/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create ui/tokens/ directory for version-controlled token artifacts
- [X] T002 [P] Install Playwright Python package and Chromium browser (pip install playwright; playwright install chromium)
- [X] T003 [P] Create scripts/ directory for CLI extraction tool
- [X] T004 [P] Add Playwright and async support to requirements.txt

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create app/schemas/theme.py with Pydantic models for DesignToken, TokenMetadata, ThemeConfiguration
- [X] T006 [P] Write unit tests for DesignToken validation (name uniqueness, status="extracted" requires value, status="unknown" requires evidence) in tests/unit/test_theme_validation.py
- [X] T007 [P] Write unit tests for TokenMetadata validation (success requires tokens_extracted>0, retry_count 0-3) in tests/unit/test_theme_validation.py
- [X] T008 Implement Pydantic models with validators in app/schemas/theme.py (pass tests from T006-T007)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Automated Token Extraction via MCP (Priority: P1) 🎯 MVP

**Goal**: Extract design tokens from https://www.epam.com/ using MCP/Playwright with zero guessing

**Independent Test**: Run extraction script, verify ui/tokens/epam.tokens.json contains computed styles with metadata

### Tests First (TDD)

- [X] T009 [US1] Write test for page load with retry logic (3 attempts, exponential backoff) in tests/unit/test_theme_extraction.py
- [X] T010 [P] [US1] Write test for CSS variable extraction with pattern filtering (--color-*, --brand-*, --font-*, --typography-*) in tests/unit/test_theme_extraction.py
- [X] T011 [P] [US1] Write test for computed style extraction (body, h1-h3, button, links) in tests/unit/test_theme_extraction.py
- [X] T012 [P] [US1] Write test for partial extraction handling (some succeed, some marked "unknown") in tests/unit/test_theme_extraction.py
- [X] T013 [P] [US1] Write test for complete token replacement (delete old files before write) in tests/unit/test_theme_extraction.py
- [X] T014 [P] [US1] Write test for FR-002 metadata validation: verify epam.tokens.json contains source_url="https://www.epam.com/", extracted_at in ISO-8601 format, retry_count 0-3, and tokens array has source_selector for each token in tests/unit/test_theme_extraction.py

### Implementation

- [X] T015 [US1] Create app/services/theme_extraction_service.py with ThemeExtractionService class structure
- [X] T016 [US1] Implement page load with retry logic and exponential backoff (1s, 2s, 4s) in theme_extraction_service.py
- [X] T017 [US1] Implement CSS variable extraction from :root with pattern filtering in theme_extraction_service.py
- [X] T018 [US1] Implement computed style extraction for body, h1-h3, button, links in theme_extraction_service.py
- [X] T019 [US1] Implement structured logging for each stage (page_load, selector_search, token_capture, file_write) in theme_extraction_service.py
- [X] T020 [US1] Implement partial extraction handling - save successful tokens, mark failures as "unknown" with evidence in theme_extraction_service.py
- [X] T021 [US1] Create scripts/extract_epam_tokens.py CLI script with argument parsing (--url, --output-dir, --verbose, --help)
- [X] T022 [US1] Implement CLI exit codes (0=success, 1=partial, 2=failure, 3=config error) in extract_epam_tokens.py
- [X] T023 [US1] Wire ThemeExtractionService to CLI script, implement timeout <30 seconds constraint

**US1 Verification**: Run `python scripts/extract_epam_tokens.py`, verify extraction completes in <30 seconds with all metadata present

---

## Phase 4: User Story 2 - Token Storage & Documentation (Priority: P2)

**Goal**: Store extracted tokens in version-controlled JSON and Markdown files

**Independent Test**: Verify ui/tokens/ contains epam.tokens.json, epam.colors.md, epam.typography.md in Git

### Tests First (TDD)

- [ ] T024 [US2] Write test for JSON file creation with correct structure (metadata + tokens) in tests/unit/test_theme_service.py
- [ ] T025 [P] [US2] Write test for Markdown color documentation generation in tests/unit/test_theme_service.py
- [ ] T026 [P] [US2] Write test for Markdown typography documentation generation in tests/unit/test_theme_service.py
- [ ] T027 [P] [US2] Write test for complete file replacement on re-extraction in tests/unit/test_theme_service.py

### Implementation

- [X] T028 [US2] Create app/services/theme_service.py with ThemeService class for file I/O operations
- [X] T029 [US2] Implement write_tokens_json() method to write ui/tokens/epam.tokens.json with DesignToken and TokenMetadata in theme_service.py
- [X] T030 [US2] Implement generate_colors_markdown() method to create ui/tokens/epam.colors.md with hex values and usage context in theme_service.py
- [X] T031 [US2] Implement generate_typography_markdown() method to create ui/tokens/epam.typography.md with font families, sizes, weights, line heights in theme_service.py
- [X] T032 [US2] Implement complete file replacement logic - delete existing files before writing new ones in theme_service.py
- [X] T033 [US2] Wire ThemeService to extraction script for file writing operations in scripts/extract_epam_tokens.py
- [ ] T034 [US2] Add token files to Git tracking (git add ui/tokens/*)

**US2 Verification**: Run extraction, verify all 3 files created, commit to Git, check `git log` shows files tracked

---

## Phase 5: User Story 3 - Backend Theme Verification (Priority: P3)

**Goal**: Backend service to load, validate, and serve extracted tokens (no frontend integration)

**Independent Test**: Start application, verify ThemeConfig loads tokens and backend methods return correct values

### Tests First (TDD)

- [ ] T035 [US3] Write test for theme configuration loader reading ui/tokens/epam.tokens.json in tests/unit/test_theme_config.py
- [ ] T036 [P] [US3] Write test for missing token file handling (raise clear error) in tests/unit/test_theme_config.py
- [ ] T037 [P] [US3] Write test for invalid JSON handling (validation error) in tests/unit/test_theme_config.py
- [ ] T038 [P] [US3] Write test for theme reload on token file update in tests/unit/test_theme_config.py

### Implementation

- [X] T039 [US3] Create app/core/theme_config.py with ThemeConfig class
- [X] T040 [US3] Implement load_tokens() method to read and parse ui/tokens/epam.tokens.json in theme_config.py
- [X] T041 [US3] Implement get_font_family() method to extract font families by element type (body, h1, h2, h3) in theme_config.py
- [X] T042 [US3] Implement get_color() method to extract colors by token name (primary, text, link) in theme_config.py
- [X] T043 [US3] Implement error handling for missing file, invalid JSON, missing required fields in theme_config.py
- [X] T044 [US3] Wire ThemeConfig into application startup (app/main.py) to load tokens on initialization
- [X] T045 [US3] Add unit test verifying ThemeConfig methods return correct token values for sample queries (body-font-family, primary-color, h1-font-size) in tests/unit/test_theme_config.py

**US3 Verification**: Start app, call ThemeConfig.get_font_family("body") and verify it returns correct value from epam.tokens.json

---

## Phase 6: User Story 4 - Visual Verification Preview (Priority: P4)

**Goal**: Preview page displaying all themed components for quick verification

**Independent Test**: Navigate to /api/theme/preview, verify all component samples rendered with EPAM theme

### Tests First (TDD)

- [ ] T046 [US4] Write integration test for GET /api/theme/preview returns 200 with HTML in tests/integration/test_theme_endpoints.py
- [ ] T047 [P] [US4] Write integration test for preview page contains all typography samples (body, h1, h2, h3) in tests/integration/test_theme_endpoints.py
- [ ] T048 [P] [US4] Write integration test for preview page contains button samples (primary, secondary, disabled) in tests/integration/test_theme_endpoints.py
- [ ] T049 [P] [US4] Write integration test for preview page contains form elements (input, textarea) in tests/integration/test_theme_endpoints.py
- [ ] T050 [P] [US4] Write integration test for 500 error when token file missing in tests/integration/test_theme_endpoints.py
- [ ] T051 [P] [US4] Write integration test for response time <5 seconds in tests/integration/test_theme_endpoints.py
- [ ] T052 [P] [US4] Write integration test for SC-004 verification: load epam.tokens.json, call preview endpoint, assert returned typography values (font-family exact match, font-weight exact match, font-size/line-height within ±1px) match token JSON values in tests/integration/test_theme_endpoints.py

### Implementation

- [X] T053 [US4] Create app/api/routes/theme.py with FastAPI router
- [X] T054 [US4] Implement GET /api/theme/preview endpoint that reads ui/tokens/epam.tokens.json
- [X] T055 [US4] Generate HTML response with inline styles from tokens (body, h1-h3, buttons, inputs, links) in theme.py
- [X] T056 [US4] Add typography samples section to preview HTML in theme.py
- [X] T057 [US4] Add button samples section (primary, secondary, disabled) to preview HTML in theme.py
- [X] T058 [US4] Add form elements section (input, textarea) to preview HTML in theme.py
- [X] T059 [US4] Add footer with metadata (token source, last updated) to preview HTML in theme.py
- [X] T060 [US4] Implement error handling for missing/invalid token file (return 500 with JSON error) in theme.py
- [X] T061 [US4] Register theme router in app/main.py

**US4 Verification**: Open http://localhost:8000/api/theme/preview, visually compare to https://www.epam.com/, verify <5s load time

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Quality assurance, documentation, and final integration

- [ ] T062 [P] Run full test suite (pytest tests/) and verify all tests pass
- [ ] T063 [P] Run coverage report (pytest --cov=app --cov-report=term-missing) and verify >80% coverage
- [ ] T064 [P] Update requirements.txt with final pinned versions
- [ ] T065 [P] Update .gitignore to exclude __pycache__, .pytest_cache if not already present
- [ ] T066 Manually test extraction end-to-end following quickstart.md guide
- [ ] T067 Manually test preview endpoint in browser, verify all components render correctly
- [ ] T068 Verify extraction completes in <30 seconds (SC-002)
- [ ] T069 Verify preview page loads in <5 seconds (SC-005)
- [ ] T070 Verify full cycle (extract→store→verify) completes in <2 minutes (SC-006)
- [ ] T071 Run tests and prepare PR with test report (pass/fail counts, coverage %) per constitution requirement

---

## Dependencies: Story Completion Order

**Blocking dependencies (must complete before others can start)**:

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundation: Pydantic schemas)
    ↓
├─ US1 (Extraction) ─────┐
    ↓                    ↓
├─ US2 (Storage) ────────┤
    ↓                    ↓
├─ US3 (Application) ────┤
    ↓                    ↓
└─ US4 (Preview) ────────┘
    ↓
Phase 7 (Polish)
```

**Parallel opportunities**:
- After Phase 2: US1, US2, US3 tests can be written in parallel
- After US1 implementation: US2, US3 implementation can proceed in parallel
- After US3: US4 can proceed independently
- Within each story: Tests marked [P] can run in parallel

**MVP Scope**: US1 + US2 = Minimum viable product (extraction + storage). US3 and US4 enhance value but aren't blocking for token extraction capability.

---

## Implementation Strategy

**Recommended approach**:
1. Complete Phase 1-2 (Setup + Foundation) first
2. Implement US1 (Extraction) completely - this delivers core value
3. Implement US2 (Storage) - completes the extraction workflow
4. **Checkpoint**: Extract real tokens, commit to Git - MVP is now functional
5. Implement US3 (Application) - applies tokens to UI
6. Implement US4 (Preview) - adds verification capability
7. Polish phase - final QA and performance validation

**Test-Driven Development**: Write tests first (T009-T013, T023-T026, etc.), watch them fail, then implement to make them pass.

---

## Task Summary

- **Total Tasks**: 71
- **Phase 1 (Setup)**: 4 tasks
- **Phase 2 (Foundation)**: 4 tasks (BLOCKING)
- **Phase 3 (US1 - Extraction)**: 15 tasks (6 tests + 9 implementation)
- **Phase 4 (US2 - Storage)**: 11 tasks (4 tests + 7 implementation)
- **Phase 5 (US3 - Backend Verification)**: 11 tasks (4 tests + 7 implementation)
- **Phase 6 (US4 - Preview)**: 16 tasks (7 tests + 9 implementation)
- **Phase 7 (Polish)**: 10 tasks

**Estimated Duration**: 
- MVP (Phase 1-2 + US1 + US2): ~2-3 days
- Full feature (All phases): ~4-5 days

**Parallel Tasks**: 28 tasks marked [P] can be executed in parallel when their dependencies are met
