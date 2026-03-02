# CLI Contract: EPAM Token Extraction Script

**Created**: 2026-03-02  
**Purpose**: Define command-line interface contract for the token extraction tool

## Command Overview

**Script**: `scripts/extract_epam_tokens.py`  
**Purpose**: Extract design tokens from https://www.epam.com/ using MCP/Playwright automation  
**Execution**: `python scripts/extract_epam_tokens.py [options]`

---

## Command Synopsis

```bash
python scripts/extract_epam_tokens.py [--url URL] [--output-dir DIR] [--verbose] [--help]
```

---

## Arguments & Options

### `--url URL`
- **Type**: String (URL)
- **Default**: `https://www.epam.com/`
- **Required**: No
- **Description**: Source website to extract tokens from
- **Validation**: Must be valid HTTP/HTTPS URL
- **Example**: `--url https://www.epam.com/careers`

### `--output-dir DIR`
- **Type**: String (directory path)
- **Default**: `ui/tokens/`
- **Required**: No
- **Description**: Directory where token files will be written
- **Validation**: Directory will be created if it doesn't exist
- **Example**: `--output-dir custom/tokens/`

### `--verbose`
- **Type**: Boolean flag
- **Default**: `false`
- **Required**: No
- **Description**: Enable verbose logging (all extraction stages with details)
- **Example**: `--verbose`

### `--help` / `-h`
- **Type**: Boolean flag
- **Description**: Display help message and exit
- **Example**: `--help`

---

## Exit Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 0 | Success | Extraction completed successfully, at least one token extracted |
| 1 | Partial Failure | Some tokens extracted, some marked as "unknown" (still writes files) |
| 2 | Total Failure | Zero tokens extracted, extraction failed after all retries |
| 3 | Configuration Error | Invalid arguments, missing dependencies, or file permission issues |

---

## Output Files

### Generated Files (on success or partial failure)

1. **`{output-dir}/epam.tokens.json`**
   - Format: JSON
   - Content: Machine-readable token data with metadata
   - Structure: See data-model.md → DesignToken, TokenMetadata

2. **`{output-dir}/epam.colors.md`**
   - Format: Markdown
   - Content: Human-readable color documentation
   - Example:
     ```markdown
     # EPAM Color Tokens
     
     Extracted: 2026-03-02T14:30:00Z
     
     ## Primary Colors
     - **primary**: `#00C1DE` (extracted from :root --brand-primary)
     - **text**: `#333333` (extracted from body color)
     ```

3. **`{output-dir}/epam.typography.md`**
   - Format: Markdown
   - Content: Human-readable typography documentation
   - Example:
     ```markdown
     # EPAM Typography Tokens
     
     Extracted: 2026-03-02T14:30:00Z
     
     ## Body Text
     - Font Family: Open Sans, sans-serif
     - Font Size: 16px
     - Line Height: 1.5
     
     ## Headings
     ### H1
     - Font Family: Roboto, sans-serif
     - Font Size: 48px
     - Font Weight: 700
     - Line Height: 1.2
     ```

---

## Standard Output (stdout)

### Structured Logging (default mode)

```
[2026-03-02 14:30:00] [INFO] Stage: Page Load | URL: https://www.epam.com/ | Duration: 2.3s | Status: 200
[2026-03-02 14:30:02] [INFO] Stage: Selector Search | Selector: :root | Found: true
[2026-03-02 14:30:03] [INFO] Stage: Token Capture | Token: --brand-primary | Value: #00C1DE | Source: :root
[2026-03-02 14:30:03] [INFO] Stage: Token Capture | Token: body-font-family | Value: Open Sans | Source: body
[2026-03-02 14:30:04] [WARN] Stage: Token Capture | Token: button-hover | Status: unknown | Reason: Hover states not extractable
[2026-03-02 14:30:05] [INFO] Stage: File Write | Path: ui/tokens/epam.tokens.json | Tokens: 12 | Success: true
[2026-03-02 14:30:05] [INFO] Extraction Complete | Total: 12 | Extracted: 11 | Unknown: 1 | Duration: 5.2s
```

### Verbose Logging (with `--verbose` flag)

Includes additional details:
- DOM selectors attempted
- Computed style properties for each element
- Retry attempts with backoff times
- File write operations with byte sizes

---

## Standard Error (stderr)

### Error Messages

```
[2026-03-02 14:30:00] [ERROR] Network Error | URL: https://www.epam.com/ | Attempt: 1/3 | Retrying in 1s...
[2026-03-02 14:30:02] [ERROR] Network Error | URL: https://www.epam.com/ | Attempt: 2/3 | Retrying in 2s...
[2026-03-02 14:30:06] [ERROR] Network Error | URL: https://www.epam.com/ | Attempt: 3/3 | Retrying in 4s...
[2026-03-02 14:30:12] [ERROR] Extraction Failed | Total attempts: 3 | Reason: Network timeout | Exit code: 2
```

---

## Behavior Specifications

### Retry Logic (per clarification Q3)
- Automatic retry on network errors: 3 attempts maximum
- Exponential backoff: 1s, 2s, 4s between retries
- Logged to stderr with attempt count

### Token Replacement (per clarification Q1)
- **Complete replacement**: Existing token files deleted before writing new results
- No merging or versioning
- Git history provides version control if needed

### Partial Results (per clarification Q5)
- Exit code 1 if some tokens fail but some succeed
- Files still written with successful tokens
- Unknown tokens listed in JSON with evidence

### Timeout
- Total execution time <30 seconds (per SC-002)
- Page load timeout: 10 seconds per attempt
- Selector search timeout: 2 seconds per selector

---

## Dependencies

### Required Python Packages
- `playwright` (browser automation)
- `pydantic` (data validation)

### Required System Components
- MCP server with Playwright support
- Chromium browser (installed via `playwright install chromium`)
- Network access to https://www.epam.com/

### Environment Variables
Optional:
- `MCP_SERVER_URL`: Override default MCP server endpoint (default: auto-detect)

---

## Usage Examples

### Basic Extraction
```bash
python scripts/extract_epam_tokens.py
```
Extracts tokens from https://www.epam.com/ to ui/tokens/

### Custom URL
```bash
python scripts/extract_epam_tokens.py --url https://www.epam.com/about
```

### Custom Output Directory with Verbose Logging
```bash
python scripts/extract_epam_tokens.py --output-dir custom/tokens/ --verbose
```

### Display Help
```bash
python scripts/extract_epam_tokens.py --help
```

---

## Testing Contract Compliance

### Unit Test Scenarios

1. **Argument Parsing**: Verify CLI arguments parsed correctly
2. **Default Values**: Test default URL and output-dir when not specified
3. **Exit Codes**: Assert correct exit code for each scenario (success/partial/failure)
4. **File Creation**: Verify all 3 files created on success

### Integration Test Scenarios

1. **End-to-End Success**: Run script against staging server → verify files created
2. **Network Failure**: Mock network timeout → verify retry logic with exponential backoff
3. **Partial Extraction**: Mock some selectors fail → verify exit code 1, files still written

### Example Test (pytest)
```python
def test_cli_success(tmp_path):
    result = subprocess.run([
        "python", "scripts/extract_epam_tokens.py",
        "--output-dir", str(tmp_path)
    ], capture_output=True)
    
    assert result.returncode == 0
    assert (tmp_path / "epam.tokens.json").exists()
    assert (tmp_path / "epam.colors.md").exists()
    assert (tmp_path / "epam.typography.md").exists()
    assert "Extraction Complete" in result.stdout.decode()
```

---

## Contract Versioning

**Current Version**: 1.0  
**Breaking Changes**: Changes to argument names, exit codes, or output file names  
**Non-Breaking Changes**: New optional arguments, additional log messages, new output files
