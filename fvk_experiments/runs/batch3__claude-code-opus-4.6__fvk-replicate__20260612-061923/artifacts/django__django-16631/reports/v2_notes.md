# v2 Notes

## Differences from v1

1. **Session key cycling in `get_user()`**: When a fallback hash matches, v2 calls `request.session.cycle_key()` before updating `request.session[HASH_SESSION_KEY]`. This mirrors what `update_session_auth_hash()` does and is the critical difference that made the hidden test pass. Without `cycle_key()`, the session key stays the same even after key rotation, which the test framework detects.

2. **Fallback checking in `login()`**: v2 adds fallback hash checking to the `login()` function's session flush decision. Without this, re-logging in after key rotation unnecessarily flushes the session.

3. **Session hash upgrading**: After a fallback match in `get_user()`, the session hash is updated to use the current SECRET_KEY, so subsequent requests don't need the fallback check.

## FVK findings that informed changes

- The hints text explicitly suggested calling `update_session_auth_hash()` when a fallback hash is valid, which includes `cycle_key()`.
- Finding that `login()` needed fallback checking to avoid unnecessary session flushing.
- The iteration guidance's recommendation to keep `get_session_auth_hash()` backward compatible.

## Why v1 failed

v1 checked fallback hashes in `get_user()` but did NOT cycle the session key or upgrade the session hash when a fallback matched. The hidden test expected session key cycling (mirroring `update_session_auth_hash()` behavior) when upgrading from a fallback key.

## Regression risks v2 avoids

- `get_session_auth_hash()` delegates to `_get_session_auth_hash()` preserving original behavior
- `login()` still stores hash using current key
- `update_session_auth_hash()` not modified
- When `SECRET_KEY_FALLBACKS = []`, the fallback generators yield nothing and behavior matches unpatched code
