# Implementation Plan: EPAM UI Theme & Typography

**Branch**: `002-epam-ui-theme` | **Date**: 2026-03-02 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-epam-ui-theme/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Extract authentic EPAM design tokens (typography and colors) from https://www.epam.com/ using MCP/Playwright browser automation. Store tokens as versioned artifacts (JSON + Markdown) and provide backend verification via preview endpoint. **Scope**: Token extraction, storage, and backend theme service only. Frontend UI integration deferred to feature 003-ui-foundation. Technical approach: evidence-based extraction (measured, not guessed) with structured logging, retry logic, and partial result handling.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI (existing), Playwright (MCP for browser automation), Pydantic (validation)
**Storage**: File system - ui/tokens/ directory for JSON and Markdown token artifacts  
**Testing**: pytest (existing), FastAPI TestClient (for preview endpoint integration tests)
**Target Platform**: Linux server (backend FastAPI application)
**Project Type**: Web service with automation tooling (MCP-based extraction script + theme application)
**Performance Goals**: Token extraction <30 seconds (SC-002), preview page load <5 seconds (SC-005), full cycle (extract→store→apply) <2 minutes (SC-006)  
**Constraints**: Must use MCP/Playwright for extraction (no guessing allowed), 3 retries with exponential backoff for network issues, complete token replacement on re-extraction
**Scale/Scope**: Single source website (https://www.epam.com/), ~10-15 design tokens (body+h1/h2/h3 typography, primary button, links, CSS variables matching --color-*/--brand-*/--font-*/--typography-*)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. Python FastAPI Stack** | ✅ PASS | Using Python 3.11+, FastAPI for preview endpoint, no DB required (file-based tokens) |
| **II. Layered Architecture** | ✅ PASS | Extraction logic in services/, token storage via file I/O, preview endpoint in app/api/routes/, no cross-layer violations |
| **III. Validation & Error Handling** | ✅ PASS | Pydantic schemas for token data structures, centralized error handling for preview endpoint and extraction failures |
| **IV. Security & Secret Hygiene** | ✅ PASS | No secrets involved; extracted tokens are public design data, stored as files in version control per requirements |
| **V. Test Discipline** | ✅ PASS | TDD for extraction logic (services), integration tests for preview endpoint using TestClient, boundary tests for retry/timeout logic |
| **VI. SpecKit Workflow** | ✅ PASS | Following specify→clarify→plan→tasks→implement workflow, this is the plan phase |
| **Evidence-Based Development** | ✅ PASS | **Constitution explicitly requires MCP extraction for UI theming** - this feature directly implements that mandate. Zero guessing, all tokens measured via Playwright |

**Result**: ✅ ALL GATES PASSED - No violations, no complexity justification needed. Feature aligns perfectly with constitution requirements, especially Evidence-Based Development mandate for UI theming.

## Project Structure

### Documentation (this feature)

```text
specs/002-epam-ui-theme/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (next)
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── contracts/           # Phase 1 output (if API endpoints added)
    └── preview-api.md   # Preview endpoint contract
```

### Source Code (repository root)

```text
app/
├── api/
│   └── routes/
│       └── theme.py            # NEW: Preview endpoint for theme verification
├── services/
│   ├── theme_extraction_service.py  # NEW: MCP/Playwright extraction logic
│   └── theme_service.py             # NEW: Token file I/O, theme application
├── schemas/
│   └── theme.py                # NEW: Pydantic models for tokens/metadata
└── core/
    └── theme_config.py         # NEW: Theme configuration loader

ui/
└── tokens/                     # NEW: Version-controlled token artifacts
    ├── epam.tokens.json        # Machine-readable tokens
    ├── epam.colors.md          # Human-readable color docs
    └── epam.typography.md      # Human-readable typography docs

tests/
├── integration/
│   └── test_theme_endpoints.py      # NEW: Preview endpoint tests
└── unit/
    ├── test_theme_extraction.py     # NEW: Extraction logic tests (TDD)
    └── test_theme_service.py        # NEW: Token I/O tests

scripts/
└── extract_epam_tokens.py      # NEW: CLI script for manual token extraction
```

**Structure Decision**: Using existing backend structure (app/). New directories: `ui/tokens/` for artifacts, new service/schema files for theme logic. Extraction script in `scripts/` for manual invocation. **No frontend changes in this feature** - this feature provides token artifacts + backend preview endpoint only. Actual UI integration deferred to feature 003-ui-foundation.

## Complexity Tracking

> **Not applicable** - No constitution violations detected. Feature follows all architectural principles and quality gates.

---

## Post-Design Constitution Re-Check

**Date**: 2026-03-02  
**Status**: ✅ ALL GATES STILL PASS

After completing design artifacts (research.md, data-model.md, contracts/, quickstart.md), re-evaluated against constitution:

| Principle | Re-Check Status | Design Notes |
|-----------|-----------------|--------------|
| **I. Python FastAPI Stack** | ✅ PASS | Design uses Python 3.11+, FastAPI for preview endpoint, no DB changes |
| **II. Layered Architecture** | ✅ PASS | Clear layers: app/api/routes/theme.py, app/services/theme_*_service.py, app/schemas/theme.py |
| **III. Validation & Error Handling** | ✅ PASS | Pydantic schemas defined for DesignToken/TokenMetadata, error contracts documented |
| **IV. Security** | ✅ PASS | No secrets, tokens are public design data stored in version control |
| **V. Test Discipline** | ✅ PASS | TDD specified in research.md, test scenarios in contracts/, quickstart has test commands |
| **VI. SpecKit Workflow** | ✅ PASS | Following plan phase, tasks phase next |
| **Evidence-Based Development** | ✅ PASS | MCP/Playwright extraction detailed in research.md, zero guessing approach maintained |

**Conclusion**: Design phase complete, no new violations introduced. All architecture decisions align with constitution principles.
