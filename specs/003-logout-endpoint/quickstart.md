# Quickstart: Logout Endpoint

## Goal
Implement a stateless `POST /api/auth/logout` endpoint that accepts authenticated requests and returns a success confirmation.

## Prerequisites
- Python virtual environment activated
- Dependencies installed from `requirements.txt`
- Existing auth system running (register, login endpoints functional)

## Validate Baseline
```bash
pytest tests/integration/test_auth_endpoints.py -q
# Expected: Existing register/login tests pass
```

## Implement Scope
1. Add logout route to `app/api/routes/auth.py`
2. Endpoint should:
   - Require authentication via `get_current_user` dependency
   - Return HTTP 200 with `{ "message": "logged out" }`
   - Return HTTP 401 for unauthenticated requests (automatic via dependency)
3. No changes needed to:
   - `app/services/auth_service.py`
   - `app/core/security.py`
   - Database schema

## Add Integration Tests
In `tests/integration/test_auth_endpoints.py`, add:
```python
def test_authenticated_logout_returns_200(client):
    """Authenticated user can logout successfully"""
    # 1. Register and login to get token
    # 2. Call POST /api/auth/logout with token
    # 3. Assert response status is 200
    # 4. Assert response contains { "message": "logged out" }

def test_unauthenticated_logout_returns_401(client):
    """Unauthenticated request to logout returns 401"""
    # 1. Call POST /api/auth/logout without token
    # 2. Assert response status is 401
```

## Run Verification
```bash
pytest tests/integration/test_auth_endpoints.py -q
# Expected: 5 existing tests + 2 new tests = 7 total, all passing
```

## Expected Outcome
- New logout endpoint available at `POST /api/auth/logout`
- Authenticated requests return 200 OK
- Unauthenticated requests return 401 Unauthorized
- All existing register/login tests continue to pass
- No changes to user database or session management

## Example: Using Logout
```bash
# 1. Register and login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
# Returns: { "access_token": "jwt-token", "token_type": "bearer" }

# 2. Use token for protected endpoint
curl -X GET http://localhost:8000/api/ideas \
  -H "Authorization: Bearer jwt-token"
# Returns: ideas list

# 3. Logout
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer jwt-token"
# Returns: { "message": "logged out" }

# 4. Token is now invalid on client side (client must discard)
# Using same token for subsequent requests will fail with 401
```

## Implementation Checklist
- [ ] Route added to auth.py
- [ ] Uses `get_current_user` dependency
- [ ] Returns 200 with `{ "message": "logged out" }`
- [ ] Unauthenticated requests return 401 (automatic)
- [ ] Integration tests added (authenticated + unauthenticated)
- [ ] All existing tests still pass
