# SPEC — SECRET_KEY_FALLBACKS for sessions

## Intended behavior change

When `SECRET_KEY` is rotated and the previous key is placed in `SECRET_KEY_FALLBACKS`, existing user sessions should remain valid during the rotation period. Currently, `get_session_auth_hash()` uses only `SECRET_KEY`, so all sessions are invalidated when the key changes.

## Formal specification

### Pre-condition
- User has an active session with `_auth_user_hash` computed using a secret key `K_old`
- `settings.SECRET_KEY = K_new` (the rotated key)
- `settings.SECRET_KEY_FALLBACKS = [K_old, ...]`

### Post-condition
- `get_user(request)` returns the authenticated user (not AnonymousUser)
- The session is NOT flushed

### Invariant: backward compatibility
- `get_session_auth_hash()` called without arguments still returns HMAC using `settings.SECRET_KEY`
- `login()` stores the session hash using `settings.SECRET_KEY` (current key)
- `update_session_auth_hash()` stores the session hash using `settings.SECRET_KEY`
- When `SECRET_KEY_FALLBACKS` is empty, behavior is identical to before the change

## Code paths affected

1. `AbstractBaseUser.get_session_auth_hash()` in `django/contrib/auth/base_user.py`
2. `get_user()` in `django/contrib/auth/__init__.py` — session hash verification
3. `login()` in `django/contrib/auth/__init__.py` — session hash comparison for flush decision

## What must NOT change

- Session hash storage format
- `login()` and `update_session_auth_hash()` always use current `SECRET_KEY`
- `PasswordResetTokenGenerator` behavior (already handles fallbacks)
- Cookie signing behavior (already handles fallbacks via `django.core.signing`)
- All existing public API signatures (backward compatible additions only)
