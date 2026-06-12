# v1 Notes

## Behavioral Change

v1 makes `get_user()` (session authentication verification) check `SECRET_KEY_FALLBACKS` when verifying the session auth hash, matching the behavior already implemented for password reset tokens and signed cookies.

Previously, rotating `SECRET_KEY` would invalidate all existing sessions even if the old key was in `SECRET_KEY_FALLBACKS`. Now sessions remain valid during key rotation.

## Files Modified

1. `django/contrib/auth/base_user.py`:
   - Added `from django.conf import settings` import
   - Refactored `get_session_auth_hash()` to delegate to `_get_session_auth_hash()`
   - Added `get_session_auth_fallback_hash()` generator that yields hashes for each fallback secret
   - Added `_get_session_auth_hash(secret=None)` that passes the `secret` kwarg to `salted_hmac()`

2. `django/contrib/auth/__init__.py`:
   - Modified `get_user()` to try fallback hashes via `any()` loop, checking `[user.get_session_auth_hash(), *user.get_session_auth_fallback_hash()]`

## Public Tests Run

- `auth_tests.test_models` — 51 tests, all pass
- `auth_tests` (full suite) — 606 tests, all pass (10 skipped)

## Why This Matches the Public Issue

The issue reports that `SECRET_KEY_FALLBACKS` is not used for sessions, causing all users to be logged out when the secret key is rotated. The fix adds fallback key checking to the session verification path, consistent with how `PasswordResetTokenGenerator.check_token()` and `Signer.unsign()` already handle fallbacks.
