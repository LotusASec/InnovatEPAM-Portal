# Research: EPAM UI Theme & Typography

**Created**: 2026-03-02  
**Purpose**: Document technology choices, patterns, and best practices for MCP-based design token extraction

## Research Questions Resolved

### 1. MCP/Playwright Browser Automation for Style Extraction

**Decision**: Use Playwright Python library via MCP server integration

**Rationale**:
- Playwright provides `page.evaluate()` for executing JavaScript in browser context to access `window.getComputedStyle()`
- Supports headless Chromium for consistent rendering and style computation
- MCP server architecture allows AI agents to invoke browser automation declaratively
- Built-in screenshot capabilities for evidence capture when tokens are "unknown"
- Network interception for monitoring page load completion

**Alternatives considered**:
- Selenium WebDriver: More verbose API, slower execution, less modern than Playwright
- Puppeteer: Node.js only, would require separate toolchain from Python backend
- Direct HTTP + CSS parsing: Cannot compute final styles, misses cascade/inheritance

**Implementation approach**:
```javascript
// Execute in browser context via page.evaluate()
const styles = window.getComputedStyle(element);
const token = {
  fontFamily: styles.fontFamily,
  fontSize: styles.fontSize,
  color: styles.color,
  // ... other properties
};
```

### 2. Retry Patterns for Network Requests

**Decision**: Exponential backoff with 3 retries (base delay 1s, multiplier 2x)

**Rationale**:
- Clarification session answer: "3 retries, exponential backoff"
- Exponential backoff prevents overwhelming the target server during transient issues
- 3 attempts balances reliability with total timeout budget (SC-002: <30 seconds)
- Backoff sequence: 1s, 2s, 4s = 7s total retry overhead + 3x page load time

**Alternatives considered**:
- Single attempt: Too fragile for production automation
- Fixed interval retries: Can amplify server load spikes
- Unlimited retries: Violates <30 second extraction time constraint

**Implementation approach**:
```python
for attempt in range(3):
    try:
        await page.goto(url, timeout=10000)
        break
    except PlaywrightTimeoutError:
        if attempt < 2:
            await asyncio.sleep(2 ** attempt)
        else:
            raise
```

### 3. CSS Computed Style Extraction Techniques

**Decision**: Multi-strategy extraction with fallback hierarchy

**Rationale**:
- **Primary**: Extract CSS custom properties from `:root` matching patterns `--color-*`, `--brand-*`, `--font-*`, `--typography-*` (clarification Q4 answer)
- **Secondary**: Compute styles directly from DOM elements (body, h1-h3, buttons, links)
- **Fallback**: Mark as "unknown" with DOM snapshot if neither strategy works

**CSS Variable Filtering**:
```javascript
// Extract only brand-relevant variables
const rootStyles = getComputedStyle(document.documentElement);
const cssVars = Array.from(document.styleSheets)
  .flatMap(sheet => Array.from(sheet.cssRules))
  .filter(rule => rule.selectorText === ':root')
  .flatMap(rule => Array.from(rule.style))
  .filter(prop => /^--(color|brand|font|typography)-/.test(prop))
  .map(prop => ({
    name: prop,
    value: rootStyles.getPropertyValue(prop).trim()
  }));
```

**Element-Specific Extraction**:
```javascript
// Fallback to computed styles from actual elements
const bodyStyles = getComputedStyle(document.body);
const h1 = document.querySelector('h1');
const button = document.querySelector('button[type="submit"], .btn-primary');
```

### 4. Token Storage Format (JSON Schema)

**Decision**: Flat structure with metadata wrapper

**Rationale**:
- Simple to parse and validate
- Metadata separated from token values for clarity
- Supports "unknown" tokens with evidence field
- Version control friendly (minimal diffs on updates)

**Schema**:
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
      "name": "body-font-size",
      "type": "typography",
      "value": "16px",
      "source_selector": "body",
      "extracted_at": "2026-03-02T14:30:00Z",
      "status": "extracted"
    },
    {
      "name": "body-line-height",
      "type": "typography",
      "value": "1.5",
      "source_selector": "body",
      "extracted_at": "2026-03-02T14:30:00Z",
      "status": "extracted"
    },
    {
      "name": "h1-font-family",
      "type": "typography",
      "value": "Roboto, sans-serif",
      "source_selector": "h1",
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

### 5. Structured Logging for Extraction Process

**Decision**: Stage-based logging with timestamps and token counts (clarification Q2 answer)

**Rationale**:
- Enables debugging when selectors fail or tokens are missing
- Progress monitoring for long extractions
- Audit trail for compliance

**Log Stages**:
1. **Stage: Page Load** - Log URL, load time, network status
2. **Stage: Selector Search** - Log each CSS selector attempted, found/not found
3. **Stage: Token Capture** - Log each token extracted with name, value, source
4. **Stage: File Write** - Log file paths, token counts, success/failure

**Log Format**:
```
[2026-03-02 14:30:00] [INFO] Stage: Page Load | URL: https://www.epam.com/ | Duration: 2.3s | Status: 200
[2026-03-02 14:30:02] [INFO] Stage: Selector Search | Selector: :root | Found: true
[2026-03-02 14:30:03] [INFO] Stage: Token Capture | Token: --brand-primary | Value: #00C1DE | Source: :root
[2026-03-02 14:30:05] [INFO] Stage: File Write | Path: ui/tokens/epam.tokens.json | Tokens: 12 | Success: true
```

### 6. Partial Extraction Handling

**Decision**: Save partial results with clear marking (clarification Q5 answer)

**Rationale**:
- Even partial tokens provide value (e.g., typography works, buttons fail)
- Prevents all-or-nothing failure mode
- "unknown" tokens with evidence enable manual review and iteration

**Behavior**:
- Successfully extracted tokens → written to JSON/Markdown
- Failed tokens → added to "unknown" array with error details
- Overall status: `success: true` if ANY tokens extracted, `success: false` if total failure

### 7. Token Update Strategy

**Decision**: Complete replacement on re-extraction (clarification Q1 answer)

**Rationale**:
- Prevents stale or conflicting tokens
- Simpler mental model than merging
- Git history provides versioning if needed

**Implementation**: Delete `ui/tokens/*.json` and `ui/tokens/*.md` before writing new extraction results

## Technology Stack Summary

| Component | Technology | Justification |
|-----------|------------|---------------|
| Browser Automation | Playwright (Python) via MCP | Required by constitution for UI theming, best-in-class for style extraction |
| HTTP Retry Logic | Exponential backoff (1s, 2s, 4s) | Balances reliability with <30s timeout constraint |
| Token Storage | JSON + Markdown | Machine-readable + human-readable, version control friendly |
| Logging |  Python `logging` module | Structured stage-based logging for debugging |
| Testing | pytest + Playwright fixtures | TDD for extraction logic, integration tests for preview endpoint |
| Theme Application | Existing styling system | No new framework; import tokens into current theme config |

## Open Questions / Future Enhancements

*None blocking for MVP. All critical decisions resolved via clarification session.*

**Future enhancements (out of scope for MVP)**:
- Spacing tokens (margins, padding)
- Shadow/elevation tokens
- Animation/transition tokens
- Icon extraction
- Multi-page extraction (not just homepage)
