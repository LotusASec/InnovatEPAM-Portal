# Quickstart: EPAM UI Theme & Typography

**Created**: 2026-03-02  
**Purpose**: Get started with EPAM theme token extraction and application

## Prerequisites

- Python 3.11+ installed
- Virtual environment activated
- MCP server with Playwright support configured
- Network access to https://www.epam.com/

## Installation

### 1. Install Dependencies

```bash
# Activate virtual environment
source .venv/bin/activate

# Install Python packages
pip install playwright pydantic

# Install Chromium browser for Playwright
playwright install chromium
```

### 2. Verify MCP Server

```bash
# Check MCP server is running (implementation-specific command)
# MCP installation/configuration per project setup
```

---

## Quick Start Guide

### Step 1: Extract Tokens from EPAM Website

```bash
# Run extraction script
python scripts/extract_epam_tokens.py

# Expected output:
# [2026-03-02 14:30:00] [INFO] Stage: Page Load | URL: https://www.epam.com/ | Duration: 2.3s
# [2026-03-02 14:30:05] [INFO] Extraction Complete | Total: 12 | Extracted: 11 | Unknown: 1
```

**Result**: Creates 3 files in `ui/tokens/`:
- `epam.tokens.json` - Machine-readable tokens
- `epam.colors.md` - Color documentation
- `epam.typography.md` - Typography documentation

### Step 2: Review Extracted Tokens

```bash
# View JSON tokens
cat ui/tokens/epam.tokens.json | python -m json.tool

# View human-readable documentation
cat ui/tokens/epam.colors.md
cat ui/tokens/epam.typography.md
```

### Step 3: Start Application with Theme

```bash
# Run FastAPI application
uvicorn app.main:app --reload

# Application automatically loads tokens from ui/tokens/epam.tokens.json
```

### Step 4: Verify Theme in Preview Page

Open browser and navigate to:
```
http://localhost:8000/api/theme/preview
```

**What to check**:
- Body text uses EPAM font family
- Headings (h1, h2, h3) match EPAM typography
- Primary button color matches EPAM brand color
- Links use EPAM link color

---

## Common Tasks

### Re-extract Tokens (When EPAM Website Updates)

```bash
# Run extraction again - completely replaces existing tokens
python scripts/extract_epam_tokens.py

# Restart application to load new tokens
# (or wait for hot-reload if using --reload flag)
```

### Extract with Verbose Logging

```bash
# See detailed extraction steps
python scripts/extract_epam_tokens.py --verbose
```

### Extract to Custom Directory

```bash
# Extract to different location
python scripts/extract_epam_tokens.py --output-dir custom/path/

# Update application config to load from custom path
```

---

## Troubleshooting

### Problem: "Network Error" during extraction

**Cause**: Cannot reach https://www.epam.com/ or network timeout

**Solution**:
```bash
# Check internet connectivity
curl -I https://www.epam.com/

# Script automatically retries 3 times with exponential backoff
# If all retries fail, check firewall/proxy settings
```

### Problem: "ThemeNotConfigured" error on preview page

**Cause**: Token files not extracted yet

**Solution**:
```bash
# Run extraction first
python scripts/extract_epam_tokens.py

# Verify files exist
ls -lh ui/tokens/
```

### Problem: Preview page loads but fonts don't match EPAM

**Cause**: Tokens extracted successfully but font files not loaded

**Solution**:
- Check browser DevTools > Network tab for font loading errors
- Verify font families in `ui/tokens/epam.tokens.json`
- Ensure application theme config correctly imports tokens

### Problem: Some tokens marked as "unknown"

**Cause**: Selectors failed or styles not extractable (e.g., hover states)

**Solution**:
```bash
# Review unknown tokens in JSON
cat ui/tokens/epam.tokens.json | jq '.tokens.unknown'

# Check evidence field for DOM snapshot or reason
# Manually adjust selectors in extraction script if needed
```

---

## Development Workflow

### 1. Feature Development Cycle

```bash
# 1. Extract latest tokens
python scripts/extract_epam_tokens.py

# 2. Apply theme to new component
# (Edit app/api/routes/your_route.py to use theme)

# 3. Verify in preview
open http://localhost:8000/api/theme/preview

# 4. Run tests
pytest tests/integration/test_theme_endpoints.py
pytest tests/unit/test_theme_extraction.py
```

### 2. Test-Driven Development for Extraction Logic

```bash
# Write failing test first
# tests/unit/test_theme_extraction.py

# Run test (should fail)
pytest tests/unit/test_theme_extraction.py -v

# Implement extraction logic
# app/services/theme_extraction_service.py

# Run test (should pass)
pytest tests/unit/test_theme_extraction.py -v
```

### 3. Local Theme Customization (for development only)

```bash
# Make local changes to tokens (NOT committed to Git)
vim ui/tokens/epam.tokens.json

# Restart app to see changes
# Use this for rapid prototyping, then re-extract to get authentic tokens
```

---

## Testing

### Run All Theme Tests

```bash
# Unit tests (extraction logic, token I/O)
pytest tests/unit/test_theme_*.py -v

# Integration tests (preview endpoint)
pytest tests/integration/test_theme_endpoints.py -v

# With coverage
pytest --cov=app.services.theme_extraction_service --cov-report=term-missing
```

### Manual Verification Checklist

- [ ] Extraction completes in <30 seconds
- [ ] All token files created (JSON + 2 Markdown)
- [ ] Preview page loads in <5 seconds
- [ ] Body text font matches EPAM site
- [ ] H1/H2/H3 fonts match EPAM site
- [ ] Primary button color matches EPAM brand color
- [ ] Links use EPAM link color

---

## Next Steps

After completing quickstart:

1. **Read contracts/** - Understand API and CLI contracts
2. **Read data-model.md** - Understand entity relationships
3. **Run `/speckit.tasks`** - Generate implementation task list
4. **Follow TDD** - Write tests first, implement second

---

## Performance Targets

Per success criteria:
- Token extraction: **<30 seconds** (SC-002)
- Preview page load: **<5 seconds** (SC-005)
- Full cycle (extract→store→apply): **<2 minutes** (SC-006)

Monitor performance:
```bash
# Time extraction
time python scripts/extract_epam_tokens.py

# Check preview response time
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/theme/preview
```

---

## Additional Resources

- **Spec**: [spec.md](spec.md) - Full feature specification
- **Research**: [research.md](research.md) - Technology decisions and patterns
- **Data Model**: [data-model.md](data-model.md) - Entity definitions
- **Contracts**: [contracts/](contracts/) - API and CLI contracts
- **Constitution**: [.specify/memory/constitution.md](../../.specify/memory/constitution.md) - Project principles
