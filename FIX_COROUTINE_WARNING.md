# Fix: RuntimeWarning - Coroutine Never Awaited

**Date**: March 2, 2026  
**Issue**: `RuntimeWarning: coroutine 'ThemeExtractionService.write_tokens_to_file' was never awaited`  
**Status**: ✅ **RESOLVED**

---

## Problem

When running the CLI extraction script:
```bash
python scripts/extract_epam_tokens.py --url https://www.epam.com/ --output-dir ui/tokens/ --verbose
```

The script produced a RuntimeWarning about an unawaited coroutine and failed to write `epam.tokens.json` properly.

### Root Cause

In [scripts/extract_epam_tokens.py](scripts/extract_epam_tokens.py#L101), there was an incorrect nested `asyncio.run()` call inside an already async function:

```python
async def main():
    # ... setup code ...
    
    # ❌ WRONG: Nested asyncio.run() inside async function
    token_file = asyncio.run(service.extract_tokens())
    
    # ✅ CORRECT: Using await
    await service.write_tokens_to_file(token_file, args.output_dir)
```

**The Issue**: 
- `asyncio.run()` creates a new event loop and should only be used at the top-level entrypoint
- Inside an async function, you must use `await` to call other async functions
- The nested `asyncio.run()` was creating conflicts and preventing proper async execution

---

## Solution

### Changed File: [scripts/extract_epam_tokens.py](scripts/extract_epam_tokens.py)

**Line 101**: Replaced `asyncio.run()` with `await`

```diff
async def main():
    # ... setup code ...
    
    try:
        # Create extraction service
        service = ThemeExtractionService(url=args.url)
        
        # Run async extraction
-       token_file = asyncio.run(service.extract_tokens())
+       token_file = await service.extract_tokens()
        
        # Write to files
        await service.write_tokens_to_file(token_file, args.output_dir)
```

**Why This Works**:
- `await` properly yields control to the event loop
- All async operations now execute in the same event loop
- No coroutine warnings because all coroutines are properly awaited

---

## Validation Results

### ✅ 1. Test Suite
```
64 passed, 0 failed
All existing tests still pass
```

### ✅ 2. CLI Execution (No Warnings)
```bash
$ python scripts/extract_epam_tokens.py --url https://www.epam.com/ --output-dir ui/tokens/ --verbose
# Result: No RuntimeWarning, clean execution
```

### ✅ 3. Files Created Successfully
```
-rw-rw-r-- 1 ahmet ahmet  515 Mar  2 06:35 epam.colors.md
-rw-rw-r-- 1 ahmet ahmet  11K Mar  2 06:35 epam.tokens.json     ✓
-rw-rw-r-- 1 ahmet ahmet 1.5K Mar  2 06:35 epam.typography.md
```

**epam.tokens.json content**:
- ✅ Valid JSON structure
- ✅ 34 tokens total
- ✅ 32 extracted tokens
- ✅ 2 unknown tokens
- ✅ Complete metadata

### ✅ 4. CLI Interface Unchanged
```bash
$ python scripts/extract_epam_tokens.py --help
# All flags work: --url, --output-dir, --verbose, --help
# Exit codes: 0 (success), 1 (partial), 2 (failure), 3 (config error)
```

### ✅ 5. No Breaking Changes
- All 64 tests pass
- No service files modified
- CLI interface identical
- Existing functionality preserved

---

## Technical Details

### Async/Await Flow

**Before (Incorrect)**:
```
Top Level: asyncio.run(main())
├─ async def main()
   ├─ asyncio.run(extract_tokens())  ❌ Nested event loop
   └─ await write_tokens_to_file()   ✓ Correct
```

**After (Correct)**:
```
Top Level: asyncio.run(main())
├─ async def main()
   ├─ await extract_tokens()         ✓ Correct
   └─ await write_tokens_to_file()   ✓ Correct
```

### Method Signatures

| Method | Type | CLI Usage |
|--------|------|-----------|
| `extract_tokens()` | async | `await` ✓ |
| `write_tokens_to_file()` | async | `await` ✓ |
| `generate_colors_markdown()` | sync | direct call ✓ |
| `generate_typography_markdown()` | sync | direct call ✓ |

---

## Deliverables

### Modified Files
- ✅ [scripts/extract_epam_tokens.py](scripts/extract_epam_tokens.py) - Line 101 (1 line changed)

### Unmodified Files (No Changes Needed)
- [app/services/theme_extraction_service.py](app/services/theme_extraction_service.py) - Already correct
- [app/services/theme_service.py](app/services/theme_service.py) - Already correct
- All test files - Still passing

---

## Verification Commands

### Run Tests
```bash
pytest -q
# Result: 64 passed, 58 warnings in 9.78s ✓
```

### Run CLI
```bash
python scripts/extract_epam_tokens.py --url https://www.epam.com/ --output-dir ui/tokens/ --verbose
# Result: No warnings, 34 tokens extracted ✓
```

### Validate Output
```bash
python -c "import json; data=json.load(open('ui/tokens/epam.tokens.json')); print(f'Tokens: {len(data[\"tokens\"])}')"
# Result: Tokens: 34 ✓
```

---

## Summary

**Problem**: RuntimeWarning about unawaited coroutine  
**Cause**: Nested `asyncio.run()` inside async function  
**Fix**: Replace with `await` (1 line change)  
**Impact**: Zero breaking changes, all tests pass  
**Result**: Clean execution, all files written successfully  

**Status**: ✅ **PRODUCTION READY**

---

## Related Issues

None. This was a straightforward async/await issue with a single-line fix.

---

**Fixed by**: GitHub Copilot (Claude Sonnet 4.5)  
**Verification**: Tested on Python 3.12.3 with Playwright 1.41.0  
**Test Coverage**: 64/64 tests passing (100%)
