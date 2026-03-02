# Feature Specification: EPAM UI Theme & Typography

**Feature Branch**: `002-epam-ui-theme`  
**Created**: 2026-03-02  
**Status**: Draft  
**Input**: User description: "Create a new feature for extracting and applying EPAM UI theme using MCP automation"

**Scope Note**: This feature focuses on **token extraction, storage, and backend verification**. Frontend UI integration (applying tokens to actual application pages) is **out of scope** and will be implemented in feature 003-ui-foundation.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Automated Token Extraction via MCP (Priority: P1)

As a developer, I need to extract design tokens from the official EPAM corporate website using browser automation, so that the application uses authentic EPAM brand styling rather than approximations or guesses.

**Why this priority**: Foundation for all theme work. Without accurate tokens, all subsequent work would be based on assumptions. This delivers immediate value by providing measured, verifiable design data.

**Independent Test**: Can be fully tested by running the MCP extraction script against https://www.epam.com/ and validating that the output JSON contains computed styles for fonts, colors, and component styles with proper metadata (source URL, timestamp, selectors).

**Acceptance Scenarios**:

1. **Given** the EPAM website is accessible, **When** the MCP extraction script runs, **Then** it captures the page's computed styles for body, headings (h1-h3), primary buttons, and links
2. **Given** the extraction process completes, **When** reviewing the output, **Then** metadata includes source_url (https://www.epam.com/), extracted_at timestamp, and CSS selectors used for each token
3. **Given** a design token cannot be reliably extracted, **When** the script encounters this situation, **Then** it records the token as "unknown" and attaches evidence (DOM snippet or screenshot reference)
4. **Given** CSS custom properties exist in :root, **When** extraction runs, **Then** all relevant brand color and typography variables are captured

---

### User Story 2 - Token Storage & Documentation (Priority: P2)

As a developer, I need extracted tokens stored in version-controlled, documented files, so that the design system is traceable, auditable, and can be reviewed by stakeholders without running code.

**Why this priority**: Enables team collaboration and design review. Provides audit trail for design decisions. Required before tokens can be consumed by the application.

**Independent Test**: Can be fully tested by verifying that ui/tokens/ directory contains epam.tokens.json (machine-readable), epam.colors.md (human-readable color documentation), and epam.typography.md (typography documentation), all checked into version control.

**Acceptance Scenarios**:

1. **Given** tokens have been extracted, **When** storing them, **Then** ui/tokens/epam.tokens.json contains complete structured data with metadata
2. **Given** color tokens are available, **When** documentation is generated, **Then** ui/tokens/epam.colors.md displays each color with its hex value and usage context
3. **Given** typography tokens are available, **When** documentation is generated, **Then** ui/tokens/epam.typography.md shows font families, sizes, weights, and line heights for each text style
4. **Given** token files are created, **When** committing to Git, **Then** all files are tracked in version control with descriptive commit message

---

### User Story 3 - Backend Theme Verification (Priority: P3)

As a developer, I need a backend service to load and validate extracted tokens, so that I can verify the token structure and prepare for future frontend integration (feature 003).

**Why this priority**: Provides backend verification layer for tokens. Enables programmatic access to theme data. Actual UI integration is out-of-scope for feature 002.

**Independent Test**: Can be fully tested by starting the application, verifying ThemeConfig loads ui/tokens/epam.tokens.json successfully, and querying token values via backend methods.

**Acceptance Scenarios**:

1. **Given** tokens are stored in ui/tokens/, **When** the application starts, **Then** ThemeConfig successfully loads and parses epam.tokens.json
2. **Given** ThemeConfig is loaded, **When** requesting a font family token, **Then** the system returns the correct value from the token file
3. **Given** ThemeConfig is loaded, **When** requesting a color token, **Then** the system returns the correct hex value from the token file
4. **Given** the token file is missing or invalid, **When** ThemeConfig attempts to load it, **Then** a clear error is raised with file path and validation details

---

### User Story 4 - Visual Verification Preview (Priority: P4)

As a developer or stakeholder, I can view a preview page showing all themed components side-by-side, so that I can quickly verify the theme is applied correctly without inspecting multiple pages.

**Why this priority**: Quality assurance and stakeholder communication. Not critical for MVP functionality but important for verification.

**Independent Test**: Can be fully tested by navigating to a dedicated preview route/page and visually confirming that it displays typography samples (body text, h1, h2, h3), button styles, input fields, and links using the EPAM theme.

**Acceptance Scenarios**:

1. **Given** the theme is applied, **When** visiting the preview page, **Then** all typography levels are displayed with sample text
2. **Given** the preview page loads, **When** viewing button samples, **Then** primary, secondary, and disabled button states are shown
3. **Given** the preview page loads, **When** viewing form elements, **Then** input fields and text areas demonstrate the theme
4. **Given** the preview page loads, **When** comparing visually to https://www.epam.com/, **Then** typography and colors are recognizably similar

---

### Edge Cases

- What happens when the EPAM website structure changes? The extraction script should fail gracefully and log which selectors failed, allowing manual investigation. Successfully extracted tokens are saved; failed tokens are marked as "unknown".
- What happens when CSS variables are not defined in :root? The script should document this limitation and fall back to extracting computed styles only.
- What happens when network access to https://www.epam.com/ fails? The extraction script should retry up to 3 times using exponential backoff, then fail with a clear error message if all retries are exhausted.
- What happens when hover states cannot be extracted? Record them as "unknown" with explanatory note and use reasonable defaults (e.g., darker shade for hover).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST use MCP (Playwright browser automation) to extract design tokens from https://www.epam.com/ by measuring computed styles, not guessing or hard-coding values
- **FR-002**: Extraction process MUST capture metadata including source_url, extracted_at timestamp, and CSS selectors used for each token
- **FR-003**: Extraction process MUST capture computed styles for: body font-family, font-size, line-height; h1/h2/h3 typography; primary button styles (background, text color, border-radius, padding); link colors
- **FR-004**: Extraction process MUST capture CSS custom properties from :root if present, filtering by naming patterns to include only brand-relevant variables matching: --color-*, --brand-*, --font-*, --typography-*
- **FR-005**: System MUST store extracted tokens in ui/tokens/epam.tokens.json as structured machine-readable data
- **FR-006**: System MUST generate ui/tokens/epam.colors.md with human-readable color documentation (hex values, usage context)
- **FR-007**: System MUST generate ui/tokens/epam.typography.md with human-readable typography documentation (font families, sizes, weights, line heights)
- **FR-008**: When a token cannot be reliably extracted, system MUST record it as "unknown" and attach evidence (DOM snippet or screenshot reference). Partial extraction results MUST be saved even if some tokens fail, ensuring all successful extractions are preserved.
- **FR-009**: Backend theme configuration service MUST load and parse extracted tokens from ui/tokens/epam.tokens.json
- **FR-010**: Theme configuration MUST be verifiable via backend methods (get_font_family, get_color) and preview endpoint (no frontend integration in this feature)
- **FR-011**: System MUST provide a backend preview endpoint displaying typography samples, button styles, form elements, and links with inline styles from tokens
- **FR-012**: All token files MUST be committed to version control
- **FR-013**: When re-extracting tokens, system MUST completely replace all existing token files (JSON and Markdown) with fresh extraction results, ensuring no stale or conflicting tokens remain
- **FR-014**: Extraction process MUST provide structured logging for each stage (page load, selector search, token capture) with timestamps and token counts to enable debugging and progress monitoring
- **FR-015**: When network errors or timeouts occur, extraction process MUST retry up to 3 times using exponential backoff before failing with a clear error message

### Key Entities

- **DesignToken**: Represents a single design decision (color, font size, spacing, etc.) with attributes: name, value, type (color/typography/spacing), source_selector, extracted_at, evidence (if unknown). Tokens are fully replaced on re-extraction (no versioning or merging).
- **TokenMetadata**: Captures extraction context with attributes: source_url, extracted_at timestamp, extraction_method, browser_version, success/failure status
- **ThemeConfiguration**: Backend service that loads and validates tokens from ui/tokens/epam.tokens.json, with attributes: token_source_path, loaded_tokens, last_updated

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Design tokens are extracted from https://www.epam.com/ with 100% of tokens either successfully captured OR explicitly marked as "unknown" with evidence - zero guesses
- **SC-002**: Token extraction process completes in under 30 seconds from script invocation to file generation
- **SC-003**: All token files (JSON + Markdown) are stored in version control and can be regenerated on demand by running the extraction script
- **SC-004**: Typography verification MUST compare computed styles against extracted token values: font-family MUST exactly match extracted token value, font-weight MUST exactly match extracted token value, font-size and line-height MUST match within ±1px tolerance. Verification MUST be done via backend preview endpoint response OR Playwright automation comparing computed styles to token JSON values.
- **SC-005**: Preview endpoint displays all themed components with inline styles from tokens and loads in under 5 seconds
- **SC-006**: Theme can be re-extracted and verified by running extraction script + preview endpoint check, completing the full cycle (extract → store → verify) in under 2 minutes

## Assumptions & Dependencies

### Dependencies

- **MCP Services**: Requires MCP server with Playwright browser automation capabilities to be installed and operational
- **Network Access**: Requires reliable internet connectivity to access https://www.epam.com/ during extraction
- **Version Control**: Project must use Git or equivalent version control system for token artifact storage
- **Frontend Integration**: Out of scope for this feature - actual UI styling system integration will be implemented in feature 003-ui-foundation

### Assumptions

- **EPAM Website Stability**: Assumes https://www.epam.com/ maintains relatively stable CSS structure; breaking changes require extraction script updates
- **Browser Compatibility**: Assumes Chromium-based browser for consistent computed style measurements
- **Token Scope**: Focuses on typography and primary colors only; excludes spacing, shadows, animations, and other design tokens
- **Update Frequency**: Assumes theme updates are infrequent (quarterly or when EPAM rebrands); not designed for real-time synchronization

## Clarifications

### Session 2026-03-02

- Q: When the EPAM website updates its design and tokens are re-extracted, how should the system handle existing tokens? → A: Replace all tokens completely - delete old tokens and write fresh extraction
- Q: What level of logging/observability is required during the token extraction process? → A: Structured - log each extraction stage (page load, selector search, token capture) with timestamps and counts
- Q: If the extraction process encounters a timeout or network issue when accessing https://www.epam.com/, what retry strategy should be used? → A: 3 retries, exponential backoff
- Q: How should the system determine which CSS variables from :root are "relevant" brand tokens? → A: Filter by naming patterns - only capture variables matching patterns like --color-*, --brand-*, --font-*, --typography-*
- Q: If extraction successfully captures some tokens but fails to extract others, should the system save partial results? → A: Save partial results - write tokens that were successfully extracted, mark failed ones as "unknown" with error details
