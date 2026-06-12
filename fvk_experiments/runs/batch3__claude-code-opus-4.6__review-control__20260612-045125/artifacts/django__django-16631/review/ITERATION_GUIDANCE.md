# Iteration Guidance: v1 → v2

## Priority Changes

### 1. Simplify `base_user.py` — add `secret` to `get_session_auth_hash` directly

Remove `_get_session_auth_hash` and `get_session_auth_fallback_hash`. Change `get_session_auth_hash` to:

```python
def get_session_auth_hash(self, secret=None):
    key_salt = "django.contrib.auth.models.AbstractBaseUser.get_session_auth_hash"
    return salted_hmac(
        key_salt,
        self.password,
        secret=secret,
        algorithm="sha256",
    ).hexdigest()
```

This is backward-compatible (default `secret=None` preserves existing behavior) and matches the pattern of passing `secret` in `_make_token_with_timestamp`.

### 2. Update `get_user()` to iterate secrets

```python
session_hash_verified = session_hash and any(
    constant_time_compare(session_hash, user.get_session_auth_hash(secret=secret))
    for secret in [None, *settings.SECRET_KEY_FALLBACKS]
)
```

Using `None` as the first element preserves the default behavior (salted_hmac uses settings.SECRET_KEY when secret is None).

Consider also upgrading the session hash when a fallback matches:
```python
if not session_hash_verified and session_hash:
    for fallback_secret in settings.SECRET_KEY_FALLBACKS:
        if constant_time_compare(session_hash, user.get_session_auth_hash(secret=fallback_secret)):
            session_hash_verified = True
            request.session[HASH_SESSION_KEY] = user.get_session_auth_hash()
            break
```

### 3. Update `login()` to check fallbacks

In the login function, the session hash comparison (line 108-111) should also use fallback checking to avoid unnecessary session flushes during key rotation.

## Regression Risks

- `get_session_auth_hash()` with no args must return identical value to before
- All callers of `get_session_auth_hash()` must still work (login, get_user, update_session_auth_hash)
- Run full `auth_tests` suite after changes
