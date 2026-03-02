# API Contract: Theme Preview Endpoint

**Created**: 2026-03-02  
**Purpose**: Define HTTP API contract for theme preview page endpoint

## Endpoint Overview

**Path**: `GET /api/theme/preview`  
**Purpose**: Serve a preview page displaying all themed components (typography, buttons, inputs, links) for visual verification  
**Authentication**: None required (public endpoint)  
**Rate Limiting**: Standard application rate limits apply

---

## Request

### HTTP Method
```
GET /api/theme/preview
```

### Headers
- `Accept: text/html` (optional, default assumed)
- No authentication headers required

### Query Parameters
None

### Request Body
None (GET request)

---

## Response

### Success Response (200 OK)

**Content-Type**: `text/html`

**Body**: HTML page with embedded theme styles and component samples

**Structure**:
```html
<!DOCTYPE html>
<html>
<head>
    <title>EPAM Theme Preview</title>
    <style>
        /* Inline styles from ui/tokens/epam.tokens.json */
        body { font-family: <extracted-font>; font-size: <extracted-size>; }
        h1 { font-family: <h1-font>; font-size: <h1-size>; font-weight: <h1-weight>; }
        /* ... other token-based styles */
    </style>
</head>
<body>
    <h1>EPAM Theme Preview</h1>
    <section>
        <h2>Typography</h2>
        <p>Body text sample...</p>
        <h1>H1 Sample</h1>
        <h2>H2 Sample</h2>
        <h3>H3 Sample</h3>
    </section>
    <section>
        <h2>Buttons</h2>
        <button class="primary">Primary Button</button>
        <button class="secondary">Secondary Button</button>
        <button disabled>Disabled Button</button>
    </section>
    <section>
        <h2>Form Elements</h2>
        <input type="text" placeholder="Text input" />
        <textarea placeholder="Textarea"></textarea>
    </section>
    <section>
        <h2>Links</h2>
        <a href="#">Sample Link</a>
    </section>
    <footer>
        <p>Token source: <code>ui/tokens/epam.tokens.json</code></p>
        <p>Last updated: <span id="last-updated">2026-03-02T14:30:00Z</span></p>
    </footer>
</body>
</html>
```

**Example Response**:
```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 2845

<!DOCTYPE html>
<html>
<head>...</head>
<body>...</body>
</html>
```

---

### Error Responses

#### 500 Internal Server Error - Token File Not Found

**Condition**: `ui/tokens/epam.tokens.json` does not exist

**Response**:
```json
{
  "error": "ThemeNotConfigured",
  "message": "Theme tokens have not been extracted yet. Run extraction script first.",
  "details": {
    "expected_file": "ui/tokens/epam.tokens.json",
    "exists": false
  }
}
```

**Content-Type**: `application/json`

#### 500 Internal Server Error - Token File Invalid

**Condition**: Token file exists but contains invalid JSON or missing required fields

**Response**:
```json
{
  "error": "InvalidTokenFile",
  "message": "Token file is malformed or missing required fields.",
  "details": {
    "file": "ui/tokens/epam.tokens.json",
    "validation_errors": ["Missing 'metadata' field", "tokens.typography is not an object"]
  }
}
```

**Content-Type**: `application/json`

---

## Behavior Specifications

### Caching
- Response can be cached based on token file modification time
- `Cache-Control: public, max-age=3600` if tokens unchanged
- No cache if token file modified recently (<5 minutes)

### Performance
- Response time must be <5 seconds (per SC-005)
- Token file read on each request (no in-memory caching for MVP)
- File read errors logged but surfaced as 500 errors

### Content
- All typography levels (body, h1, h2, h3) must be displayed
- Button states (primary, secondary, disabled) must be shown
- At least one form element (input or textarea) must be displayed
- At least one link must be displayed
- Footer metadata (token source, last updated) must be present

---

## Contract Versioning

**Current Version**: 1.0  
**Breaking Changes**: Changes to endpoint path, required query parameters, or response structure major=breaking  
**Non-Breaking Changes**: Additional query parameters (optional), new response fields (additive)

---

## Testing Contract Compliance

### Integration Test Scenarios

1. **Happy Path**: Token file exists and valid → returns 200 with HTML containing all component samples
2. **Missing Token File**: Token file does not exist → returns 500 with JSON error
3. **Invalid Token File**: Token file has malformed JSON → returns 500 with JSON error
4. **Performance**: Response time <5 seconds (load time assertion)

### Example Test (pytest + TestClient)
```python
def test_preview_endpoint_with_valid_tokens(client, mock_token_file):
    response = client.get("/api/theme/preview")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<h1>EPAM Theme Preview</h1>" in response.text
    assert "ui/tokens/epam.tokens.json" in response.text

def test_preview_endpoint_missing_tokens(client):
    response = client.get("/api/theme/preview")
    assert response.status_code == 500
    assert response.json()["error"] == "ThemeNotConfigured"
```

---

## Dependencies

- Requires `ui/tokens/epam.tokens.json` to exist and be valid
- Requires theme configuration loader (`app/core/theme_config.py`)
- No external API dependencies
