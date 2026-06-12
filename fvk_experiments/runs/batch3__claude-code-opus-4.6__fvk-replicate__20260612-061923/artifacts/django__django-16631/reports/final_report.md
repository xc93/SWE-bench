# Final Report — django__django-16631

## 1. Instance summary

**Issue**: `SECRET_KEY_FALLBACKS` is not used for sessions. When rotating `SECRET_KEY` and placing the old key in `SECRET_KEY_FALLBACKS`, all existing user sessions are invalidated because `AbstractBaseUser.get_session_auth_hash()` only computes the hash with the current `SECRET_KEY`, and `auth.get_user()` only verifies against the current key's hash.

**Fix**: Add fallback hash verification in `auth.get_user()` and `auth.login()`, with session key cycling and hash upgrading when a fallback key matches. Add `get_session_auth_fallback_hash()` and `_get_session_auth_hash()` helper methods to `AbstractBaseUser`.

## 2. v1 patch summary

v1 added `get_session_auth_fallback_hash()` to `AbstractBaseUser` and modified `get_user()` in `django/contrib/auth/__init__.py` to check fallback hashes when the primary hash verification failed. It refactored `get_session_auth_hash()` to delegate to `_get_session_auth_hash(secret=None)`.

**v1 score**: FAIL_TO_PASS 0/1, PASS_TO_PASS 12/12, resolved=false

## 3. FVK analysis summary

Key findings from FVK analysis (Phase 3):
- **Finding 2**: v1 did not modify `login()`, missing a code path for fallback checking during re-login
- **Finding 5**: `login()` needs fallback checking to avoid unnecessary session flushing on re-login after key rotation
- **Finding 6**: Session hash upgrading was identified as potentially expected behavior, citing the issue discussion hint about calling `update_session_auth_hash()` when a fallback hash is valid

The iteration guidance recommended modifying both `login()` and `get_user()`, adding session hash upgrading, and keeping `get_session_auth_hash()` backward compatible.

## 4. v2 patch summary

v2 made three additions beyond v1:

1. **Session key cycling (`cycle_key()`)**: When a fallback hash matches in `get_user()`, `request.session.cycle_key()` is called before updating the session hash. This mirrors `update_session_auth_hash()` behavior and was the critical missing piece.

2. **Session hash upgrading**: After fallback match, `request.session[HASH_SESSION_KEY]` is updated to the current key's hash, so subsequent requests use the primary key directly.

3. **`login()` fallback checking**: Added fallback hash verification in `login()`'s session flush decision to prevent unnecessary session flushing when re-logging in after key rotation.

**v2 score**: FAIL_TO_PASS 1/1, PASS_TO_PASS 12/12, resolved=true

## 5. Difference analysis

| Aspect | v1 | v2 |
|--------|----|----|
| `base_user.py` changes | `_get_session_auth_hash` + `get_session_auth_fallback_hash` | Same |
| `get_user()` fallback check | Yes | Yes |
| `login()` fallback check | No | Yes |
| Session hash upgrading | No | Yes |
| Session key cycling (`cycle_key()`) | No | **Yes** (critical) |

The critical difference was `request.session.cycle_key()`. The hidden test expected session key cycling when upgrading from a fallback key, consistent with the hint that suggested calling `update_session_auth_hash()`.

## 6. FVK usefulness assessment

**Did FVK help?** Partially. FVK correctly identified that `login()` needed modification (Finding 2/5) and that session hash upgrading was likely needed (Finding 6), citing the issue hint about `update_session_auth_hash()`. However, FVK did not explicitly call out `cycle_key()` as the critical missing behavior. The hint about `update_session_auth_hash()` was present in the problem statement's discussion section, but FVK's iteration guidance didn't directly translate this into "call `cycle_key()`."

**What FVK got right**:
- Identified that `login()` was a missing code path
- Identified that session hash upgrading was needed
- Referenced `update_session_auth_hash()` as the model to follow

**What FVK missed**:
- Did not explicitly identify `cycle_key()` as the critical missing behavior
- Multiple intermediate v2 attempts (without `cycle_key()`) all failed, suggesting FVK's guidance wasn't specific enough about this detail

**Net assessment**: FVK provided directional guidance that eventually led to the solution, but required significant trial and error (7 failed attempts before success). The key insight came from carefully re-reading the hint about `update_session_auth_hash()` and realizing it includes `cycle_key()`.
