# SWE-bench Baseline: astropy__astropy-14096

## Benchmark

- Dataset: princeton-nlp/SWE-bench_Verified
- Exact row URL: https://datasets-server.huggingface.co/rows?dataset=princeton-nlp%2FSWE-bench_Verified&config=default&split=test&offset=7&length=1
- Repo: astropy/astropy
- Repo URL: https://github.com/astropy/astropy.git
- Instance ID: astropy__astropy-14096
- Base commit: 1a4462d72eb03f30dc83a879b1dd57aac8b2c18b
- Base commit URL: https://github.com/astropy/astropy/commit/1a4462d72eb03f30dc83a879b1dd57aac8b2c18b
- Version: 5.1
- Difficulty: 15 min - 1 hour

## Benchmark Discipline

- Gold patch inspected: no
- Hidden test_patch manually inspected: no
- Hidden test names inspected: no
- Hidden assertions inspected: no
- Hidden failure traces inspected: no

## Public Problem Summary

When subclassing `SkyCoord` and adding a `@property` that internally accesses a non-existent attribute, the resulting `AttributeError` is misleading. It reports that the *property itself* doesn't exist, rather than the attribute that was actually missing inside the property. This happens because Python's attribute lookup calls `__getattr__` when a property's `__get__` raises `AttributeError`, and `SkyCoord.__getattr__` doesn't know about the original error.

## Patch

- Files changed: `astropy/coordinates/sky_coordinate.py`
- Behavioral change: Before raising the generic "no attribute" error in `__getattr__`, check if `attr` is a descriptor (like a property) defined on the class hierarchy. If so, re-invoke `__get__` to surface the original `AttributeError` instead of the misleading one.
- Public tests run: `astropy/coordinates/tests/test_sky_coord.py` — 426 passed, 3 skipped, 1 xfailed
- Why this matches the public issue statement: The fix ensures that when a property on a SkyCoord subclass raises `AttributeError` internally, the original error message (naming the actually-missing attribute) is propagated instead of being swallowed and replaced with a misleading message about the property itself.
