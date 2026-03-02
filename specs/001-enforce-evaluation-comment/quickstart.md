# Quickstart: Evaluation Status Rule Enforcement

## Goal
Ensure status update endpoint enforces comment requirement for `accepted`/`rejected` via service layer and preserves non-admin `403` behavior.

## Prerequisites
- Python virtual environment activated
- Dependencies installed from `requirements.txt`

## Validate Baseline
```bash
pytest -q
```

## Implement Scope
1. Update API status route to delegate status-update decisions to evaluation service.
2. Ensure route passes `status` and `comment` payload to service.
3. Keep admin dependency at route level.

## Add/Adjust Integration Tests
In `tests/integration/test_evaluation_endpoints.py`, verify:
1. admin can set `under_review` without comment -> `200`
2. admin cannot set `accepted` without comment -> `400`
3. admin cannot set `rejected` without comment -> `400`
4. non-admin cannot update status -> `403`

## Run Verification
```bash
pytest -q
pytest tests/integration/test_evaluation_endpoints.py -q
```

## Expected Outcome
- All tests pass.
- HTTP layer cannot bypass accepted/rejected comment rule.
- Out-of-scope modules unaffected.
