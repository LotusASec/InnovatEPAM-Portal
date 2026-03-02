# Data Model: EPAM UI Theme & Typography

**Created**: 2026-03-02  
**Purpose**: Define entities, their attributes, relationships, and state transitions for theme token extraction and application

## Entities

### 1. DesignToken

**Description**: Represents a single design decision (color, font size, spacing, etc.) extracted from the EPAM website.

**Attributes**:
- `name` (string, required): Token identifier (e.g., "body-font-family", "h1-font-size", "primary-color")
- `value` (string, required): Token value (e.g., "Open Sans, sans-serif", "48px", "#00C1DE")
- `type` (enum, required): Category of token - "typography" | "color" | "spacing"
- `source_selector` (string, required): CSS selector or method used to extract this token (e.g., "body", ":root --brand-primary", "h1")
- `extracted_at` (ISO 8601 timestamp, required): When this token was captured
- `status` (enum, required): "extracted" | "unknown"
- `evidence` (string, optional): DOM snippet or screenshot reference when status = "unknown"
- `fallback` (string, optional): Suggested fallback value when status = "unknown"

**Validation Rules**:
- `name` must be unique within a token collection
- `value` must be non-empty string when status = "extracted"
- `evidence` is required when status = "unknown"
- `type` must be one of the defined enum values

**Relationships**:
- Belongs to exactly one TokenMetadata (extraction session)
- Loaded by ThemeConfiguration for backend verification

**State Transitions**:
```
[New Token] → [Extraction Attempted]
    ↓ Success                    ↓ Failure
[status: extracted]      [status: unknown, evidence: <reason>]
    ↓
[Written to JSON/Markdown]
    ↓
[Loaded by ThemeConfiguration] (backend verification)
```

---

### 2. TokenMetadata

**Description**: Captures context about an extraction session, including source, timing, and overall success.

**Attributes**:
- `source_url` (URL string, required): Website from which tokens were extracted (always "https://www.epam.com/" for MVP)
- `extracted_at` (ISO 8601 timestamp, required): Extraction session timestamp
- `extraction_method` (string, required): Method used (e.g., "playwright-mcp", "manual")
- `browser_version` (string, required): Browser used for extraction (e.g., "Chromium 119.0")
- `success` (boolean, required): Overall extraction success (true if ANY tokens extracted)
- `tokens_extracted` (integer, required): Count of successfully extracted tokens
- `tokens_unknown` (integer, required): Count of tokens marked as "unknown"
- `extraction_duration_seconds` (float, optional): Total time for extraction
- `retry_count` (integer, optional): Number of retries attempted (0-3)

**Validation Rules**:
- `source_url` must be valid URL format
- `tokens_extracted + tokens_unknown` should equal total tokens attempted
- `success = true` requires `tokens_extracted > 0`
- `retry_count` must be 0-3 (per clarification Q3)

**Relationships**:
- Has many DesignTokens (one-to-many)
- One metadata record per extraction session

**State Transitions**:
```
[Extraction Started] → [Page Load] → [Token Capture] → [Complete]
         ↓                  ↓               ↓               ↓
    retry_count=0     retry on fail    tokens counted   success set
```

---

### 3. ThemeConfiguration

**Description**: Backend service that loads and validates extracted design tokens from the file system. Provides programmatic access to token values for verification and future integration. Does not apply styles to UI (deferred to feature 003-ui-foundation).

**Attributes**:
- `token_source_path` (file path, required): Path to token JSON file (e.g., "ui/tokens/epam.tokens.json")
- `loaded_tokens` (list of DesignToken, required): Array of DesignToken objects loaded from JSON file
- `last_updated` (ISO 8601 timestamp, required): When tokens were last loaded from file

**Validation Rules**:
- `token_source_path` must exist and be readable
- `loaded_tokens` must contain at least one token with status="extracted"
- `last_updated` should be >= token file modification time
- File must contain valid JSON matching TokenMetadata + DesignToken[] schema

**Relationships**:
- Reads tokens from TokenMetadata/DesignToken (via file I/O)
- One configuration instance per application startup

**State Transitions**:
```
[Token File Updated] → [Configuration Reads File] → [Validates Schema] → [Tokens Available]
                              ↓                           ↓                     ↓
                       last_updated set            parse JSON array      get_font_family()
                                                                          get_color()
```

---

## Entity Relationships Diagram

```
TokenMetadata (1) ----< has many >---- (N) DesignToken
      ↓                                        ↓
  metadata object                       tokens array
      ↓                                        ↓
      └─────────< stored in JSON >────────────┘
                      ↓
          ui/tokens/epam.tokens.json
                      ↓
              ThemeConfiguration (loads and validates)
                      ↓
              Backend verification methods
              (get_font_family, get_color)
```

---

## Data Flow

### Extraction Flow
1. User invokes extraction script
2. Structured logging emitted for each stage (page_load, selector_search, token_capture, file_write) per FR-014
3. TokenMetadata created with session info
4. For each design element (body, h1, button, etc.):
   - DesignToken created
   - Extraction attempted via Playwright
   - Token status set to "extracted" or "unknown"
5. All tokens + metadata written to `ui/tokens/epam.tokens.json`
6. Human-readable documentation generated to `ui/tokens/epam.colors.md` and `epam.typography.md`

### Backend Verification Flow
1. Application startup or theme reload event
2. ThemeConfiguration reads `ui/tokens/epam.tokens.json`
3. Validates JSON schema (metadata + tokens array)
4. Loads tokens into `loaded_tokens` array
5. Sets `last_updated` timestamp
6. Backend methods available for querying (get_font_family, get_color)

### Re-extraction Flow (Complete Replacement per clarification Q1)
1. User invokes extraction script
2. **Delete** existing `ui/tokens/*.json` and `*.md` files
3. Follow normal extraction flow
4. New tokens completely replace old tokens
5. ThemeConfiguration detects file change and reloads

---

## Validation Scenarios

### Scenario 1: Successful Full Extraction
- Input: EPAM website accessible, all selectors found
- Output: TokenMetadata with `success=true`, 12-15 DesignTokens with `status="extracted"`, zero tokens with `status="unknown"`

### Scenario 2: Partial Extraction (per clarification Q5)
- Input: EPAM website accessible, some selectors fail (e.g., button not found)
- Output: TokenMetadata with `success=true`, 8 DesignTokens with `status="extracted"`, 4 DesignTokens with `status="unknown"` + evidence

### Scenario 3: Total Failure
- Input: Network timeout after 3 retries
- Output: TokenMetadata with `success=false`, `retry_count=3`, error logged, no token files written

### Scenario 4: Backend Verification with Missing Token
- Input: ThemeConfiguration loads token file, backend query requests "secondary-color" token not present in JSON
- Output: Warning logged with missing token name, method returns `None` for missing value, validation passes but flags incomplete token set

---

## Storage Format

All entities persisted as JSON in `ui/tokens/epam.tokens.json` using flat array structure:

```json
{
  "metadata": {
    "source_url": "https://www.epam.com/",
    "extracted_at": "2026-03-02T14:30:00Z",
    "extraction_method": "playwright-mcp",
    "browser_version": "Chromium 119.0",
    "success": true,
    "tokens_extracted": 12,
    "tokens_unknown": 1,
    "retry_count": 0
  },
  "tokens": [
    {
      "name": "body-font-family",
      "type": "typography",
      "value": "Open Sans, sans-serif",
      "source_selector": "body",
      "extracted_at": "2026-03-02T14:30:00Z",
      "status": "extracted"
    },
    {
      "name": "h1-font-size",
      "type": "typography",
      "value": "48px",
      "source_selector": "h1",
      "extracted_at": "2026-03-02T14:30:00Z",
      "status": "extracted"
    },
    {
      "name": "primary-color",
      "type": "color",
      "value": "#00C1DE",
      "source_selector": ":root --brand-primary",
      "extracted_at": "2026-03-02T14:30:00Z",
      "status": "extracted"
    },
    {
      "name": "button-hover-color",
      "type": "color",
      "value": null,
      "source_selector": "button:hover",
      "extracted_at": "2026-03-02T14:30:00Z",
      "status": "unknown",
      "evidence": "Hover states not extractable via computed styles",
      "fallback": "Darken primary by 10%"
    }
  ]
}
```

Human-readable documentation in separate Markdown files (`epam.colors.md`, `epam.typography.md`) for stakeholder review.
