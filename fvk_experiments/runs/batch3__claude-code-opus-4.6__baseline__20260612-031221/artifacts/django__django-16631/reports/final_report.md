# SWE-bench Baseline: django__django-16631

## Benchmark

- Dataset: princeton-nlp/SWE-bench_Verified
- Exact row URL: https://datasets-server.huggingface.co/rows?dataset=princeton-nlp%2FSWE-bench_Verified&config=default&split=test&offset=236&length=1
- Repo: django/django
- Repo URL: https://github.com/django/django.git
- Instance ID: django__django-16631
- Base commit: 9b224579875e30203d079cc2fee83b116d98eb78
- Base commit URL: https://github.com/django/django/commit/9b224579875e30203d079cc2fee83b116d98eb78
- Version: 5.0
- Difficulty: 1-4 hours

## Benchmark Discipline

- Gold patch inspected: no
- Hidden test_patch manually inspected: no
- Hidden test names inspected: no
- Hidden assertions inspected: no
- Hidden failure traces inspected: no

## Public Problem Summary

When rotating SECRET_KEY and placing the old key in SECRET_KEY_FALLBACKS, all user sessions are invalidated because `AbstractBaseUser.get_session_auth_hash()` only uses the current SECRET_KEY (via `salted_hmac` default). The `get_user()` function in `django.contrib.auth` only compares the stored session hash against the hash generated with the current key, not fallback keys. This contradicts the documented behavior that SECRET_KEY_FALLBACKS should allow graceful key rotation without logging out users.

## Patch

- Files changed:
  - `django/contrib/auth/base_user.py` — Added `get_session_auth_fallback_hash()` generator method and `_get_session_auth_hash(secret=None)` private method. `get_session_auth_hash()` now delegates to `_get_session_auth_hash()`. The fallback method yields hashes for each key in `settings.SECRET_KEY_FALLBACKS`.
  - `django/contrib/auth/__init__.py` — Updated `get_user()` to check session hash against both the current key's hash and all fallback key hashes when verifying a session.
- Behavioral change: Sessions created with an old SECRET_KEY that is now in SECRET_KEY_FALLBACKS will remain valid instead of being flushed. This matches the documented behavior of SECRET_KEY_FALLBACKS.
- Public tests run: 606 auth tests, all passing (10 skipped)
- Why this matches the public issue statement: The issue reports that SECRET_KEY_FALLBACKS is not consulted when validating session auth hashes. This patch adds fallback key checking in the session verification path, following the same pattern used by `PasswordResetTokenGenerator` for token validation.
