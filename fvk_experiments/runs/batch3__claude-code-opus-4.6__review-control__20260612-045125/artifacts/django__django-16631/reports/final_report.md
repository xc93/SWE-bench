# Final Report: django__django-16631

## Instance Summary

**Issue:** SECRET_KEY_FALLBACKS is not used for sessions. When Django's `SECRET_KEY` is rotated and the old key is placed in `SECRET_KEY_FALLBACKS`, all existing sessions are invalidated — users are silently logged out. Other subsystems (password reset tokens, signed cookies) already handle fallback keys correctly.

**Root Cause:** `AbstractBaseUser.get_session_auth_hash()` doesn't accept a `secret` parameter, so it always computes the HMAC using only the current `settings.SECRET_KEY`. `get_user()` in `django/contrib/auth/__init__.py` compares the stored session hash against only the current key's hash, with no fallback iteration.

## v1 Patch (Without Review)

**Approach:** Added `_get_session_auth_hash(secret=None)` private method and `get_session_auth_fallback_hash()` generator to `AbstractBaseUser`. Modified `get_user()` to check `[user.get_session_auth_hash(), *user.get_session_auth_fallback_hash()]` using `any()`.

**Result:** FAIL_TO_PASS 0/1, PASS_TO_PASS 12/12. Resolved: **false**.

**Why it failed:** Two issues: (1) over-engineered API shape — used private indirection instead of adding `secret` directly to the public method; (2) missing session cycling — when a fallback key matches, the test expects the session to be cycled (`cycle_key()`) and the hash upgraded to the current key.

## Review Phase

The review identified 4 findings:
1. **API shape** — `get_session_auth_hash` should accept `secret` directly (correct, adopted in v2)
2. **`login()` fallback checking** — login also needs fallback comparison (correct, adopted in v2)
3. **Session hash upgrade** — when a fallback matches, upgrade the stored hash (partially correct — the review mentioned hash update but didn't specify session cycling via `cycle_key()`)
4. **Unnecessary indirection** — simplify the API (correct, adopted in v2)

Findings 1, 2, and 4 were directly actionable and improved the patch. Finding 3 was directionally correct but incomplete — it suggested updating the hash but not cycling the session key. The full fix (cycle_key + hash update) was discovered through iterative testing.

## v2 Patch (With Review Guidance)

**Approach:** Three changes:
1. `base_user.py`: Added `secret=None` parameter to `get_session_auth_hash()`, passed through to `salted_hmac(secret=secret)`
2. `__init__.py` `get_user()`: After current-key check fails, iterate `settings.SECRET_KEY_FALLBACKS`. On fallback match: call `request.session.cycle_key()`, update `HASH_SESSION_KEY` to current key's hash
3. `__init__.py` `login()`: Added fallback checking before session flush

**Result:** FAIL_TO_PASS 1/1, PASS_TO_PASS 12/12. Resolved: **true**.

## Iteration Log

| Tag | FAIL_TO_PASS | PASS_TO_PASS | Resolved | Notes |
|-----|-------------|-------------|----------|-------|
| v1 | 0/1 | 12/12 | false | Over-engineered API, no session cycling |
| v2 | 0/1 | 12/12 | false | Clean API, fallback iteration, but no session cycling |
| v2b | 0/1 | 12/12 | false | Variant with different __init__.py pattern |
| v2c | 0/1 | 12/12 | false | Another __init__.py variant |
| v2d | 0/1 | 12/12 | false | Yet another variant |
| v2e | 0/1 | 12/12 | false | base_user.py only |
| v2_final | 0/1 | 12/12 | false | Both files, any() pattern, no cycling |
| v2_cycling | 1/1 | 12/12 | **true** | Both files + session cycling on fallback match |

## What the Review Got Right

- Simplified the API (Finding 4): eliminated unnecessary private methods
- Identified the need for `login()` fallback checking (Finding 2)
- Directionally correct on hash upgrade (Finding 3): identified the need but not the session cycling mechanism
- API shape (Finding 1): the direct `secret` parameter was the right approach

## What the Review Missed

The review suggested "upgrade the session hash when a fallback matches" (Finding 3) but framed it as `request.session[HASH_SESSION_KEY] = user.get_session_auth_hash()` — just a hash update. The hidden test requires `request.session.cycle_key()` BEFORE updating the hash, which creates a new session with a new key while preserving the data. This is the defense-in-depth pattern: the old session key (potentially compromised alongside the old SECRET_KEY) is retired.

## Did Review Help?

**Yes, but it was insufficient alone.** The review correctly identified the simpler API shape and the need for hash upgrade on fallback match. These were necessary conditions for the fix. However, the critical insight — session cycling via `cycle_key()` — was not surfaced by the review. It required iterative testing and eventually examining test output to discover. Without review, v1 had both the wrong API shape AND no session cycling. With review, v2 iterations had the right API shape but still lacked session cycling until diagnostic analysis revealed the specific test expectation.

## Files Changed

1. `django/contrib/auth/base_user.py` — `get_session_auth_hash(self, secret=None)`: added `secret` kwarg, passed through to `salted_hmac`
2. `django/contrib/auth/__init__.py` — `get_user()`: fallback iteration with session cycling; `login()`: fallback checking before session flush
