# ITERATION GUIDANCE — v1 → v2

## Summary
v1 passes all 12 regression tests but fails the 1 bug-revealing test (0/1). The core concept is correct, but the implementation likely doesn't match the expected API or is missing a code path.

## Changes for v2

### Change 1: Simplify base_user.py — single method with optional `secret` parameter
**Priority: HIGH**
Replace the three-method approach (get_session_auth_hash + get_session_auth_fallback_hash + _get_session_auth_hash) with a single clean modification:

```python
def get_session_auth_hash(self):
    key_salt = "django.contrib.auth.models.AbstractBaseUser.get_session_auth_hash"
    return salted_hmac(
        key_salt,
        self.password,
        algorithm="sha256",
    ).hexdigest()

def get_session_auth_fallback_hash(self):
    for fallback_secret in settings.SECRET_KEY_FALLBACKS:
        yield salted_hmac(
            "django.contrib.auth.models.AbstractBaseUser.get_session_auth_hash",
            self.password,
            secret=fallback_secret,
            algorithm="sha256",
        ).hexdigest()
```

Keep `get_session_auth_hash()` signature unchanged (no new parameter) for maximum backward compatibility. But add `get_session_auth_fallback_hash()` as a public method.

### Change 2: Simplify get_user() fallback check
**Priority: HIGH**
Use `settings.SECRET_KEY_FALLBACKS` directly instead of `hasattr` guard:

```python
session_hash_verified = session_hash and (
    constant_time_compare(session_hash, user.get_session_auth_hash())
    or (
        hasattr(user, "get_session_auth_fallback_hash")
        and any(
            constant_time_compare(session_hash, fallback_hash)
            for fallback_hash in user.get_session_auth_fallback_hash()
        )
    )
)
```

When a fallback matches, update the session hash to the current key:
```python
if not session_hash_verified and session_hash:
    if hasattr(user, "get_session_auth_fallback_hash"):
        for fallback_hash in user.get_session_auth_fallback_hash():
            if constant_time_compare(session_hash, fallback_hash):
                session_hash_verified = True
                request.session[HASH_SESSION_KEY] = user.get_session_auth_hash()
                break
```

### Change 3: Update login() to check fallback hashes
**Priority: MEDIUM**
In `login()`, check fallback hashes before flushing:

```python
if _get_user_session_key(request) != user.pk or (
    session_auth_hash
    and not constant_time_compare(
        request.session.get(HASH_SESSION_KEY, ""), session_auth_hash
    )
    and (
        not hasattr(user, "get_session_auth_fallback_hash")
        or not any(
            constant_time_compare(
                request.session.get(HASH_SESSION_KEY, ""),
                fallback_hash,
            )
            for fallback_hash in user.get_session_auth_fallback_hash()
        )
    )
):
    request.session.flush()
```

## Forbidden changes (regression risk)
- Do NOT change how `login()` stores the session hash (must use current key)
- Do NOT change `update_session_auth_hash()` behavior
- Do NOT change `PasswordResetTokenGenerator` (already works correctly)
- Do NOT change `salted_hmac()` signature or defaults
- Do NOT modify cookie signing behavior
