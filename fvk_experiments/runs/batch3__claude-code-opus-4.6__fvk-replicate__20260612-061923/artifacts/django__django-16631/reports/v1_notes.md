# v1 Notes

## Behavior change

v1 makes `SECRET_KEY_FALLBACKS` work for session authentication. Previously, when `SECRET_KEY` was rotated and the old key placed in `SECRET_KEY_FALLBACKS`, all existing sessions were invalidated because the session auth hash was only computed and verified using the current `SECRET_KEY`.

Now, when verifying a session in `get_user()`, if the hash doesn't match with the current key, fallback keys are also tried.

## Files modified

1. `django/contrib/auth/base_user.py`:
   - Added `from django.conf import settings` import
   - Refactored `get_session_auth_hash()` to delegate to `_get_session_auth_hash()`
   - Added `get_session_auth_fallback_hash()` generator that yields hashes for each fallback key
   - Added `_get_session_auth_hash(secret=None)` that accepts an optional secret parameter

2. `django/contrib/auth/__init__.py`:
   - Modified `get_user()` to check `get_session_auth_fallback_hash()` when the primary hash doesn't match

## Public tests run

- `auth_tests.test_tokens`: 11 tests OK
- `auth_tests` (full suite): 606 tests OK (10 skipped)

## Why v1 matches the public issue

The issue reports that `SECRET_KEY_FALLBACKS` is not used for sessions - when rotating SECRET_KEY, users get logged out despite having the old key in fallbacks. v1 fixes this by checking fallback keys during session verification, mirroring how `PasswordResetTokenGenerator.check_token()` already checks fallbacks.
