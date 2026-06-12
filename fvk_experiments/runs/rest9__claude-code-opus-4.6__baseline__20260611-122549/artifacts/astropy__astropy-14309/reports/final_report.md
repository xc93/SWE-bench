# SWE-bench Baseline: astropy__astropy-14309

## Benchmark

- Dataset: princeton-nlp/SWE-bench_Verified
- Exact row URL: https://datasets-server.huggingface.co/rows?dataset=princeton-nlp%2FSWE-bench_Verified&config=default&split=test&offset=9&length=1
- Repo: astropy/astropy
- Repo URL: https://github.com/astropy/astropy.git
- Instance ID: astropy__astropy-14309
- Base commit: cdb66059a2feb44ee49021874605ba90801f9986
- Base commit URL: https://github.com/astropy/astropy/commit/cdb66059a2feb44ee49021874605ba90801f9986
- Version: 5.1
- Difficulty: <15 min fix

## Benchmark Discipline

- Gold patch inspected: no
- Hidden test_patch manually inspected: no
- Hidden test names inspected: no
- Hidden assertions inspected: no
- Hidden failure traces inspected: no

## Public Problem Summary

The `is_fits` function in `astropy/io/fits/connect.py` raises an `IndexError: tuple index out of range` when called via `identify_format` with an empty `args` tuple and a non-FITS filepath. The function unconditionally accesses `args[0]` on line 72, but `args` can be empty when `filepath` is a string that doesn't match FITS extensions and no positional arguments are provided. This was introduced by a prior refactor (commit 2a0c5c6) that changed the control flow so the `isinstance(args[0], ...)` line is reached even when `args` is empty.

## Patch

- Files changed: `astropy/io/fits/connect.py`
- Behavioral change: Guard the `args[0]` access with `if args:` check; return `False` when `args` is empty and no other condition matched.
- Public tests run:
  - `astropy/io/fits/tests/test_connect.py` — 141 passed, 8 skipped, 5 xfailed
  - `astropy/io/registry/tests/` — 231 passed, 14 skipped
- Why this matches the public issue statement: The issue reports that `identify_format("write", Table, "bububu.ecsv", None, [], {})` raises `IndexError` because `is_fits` accesses `args[0]` when `args` is empty. The fix adds a guard so that `args[0]` is only accessed when `args` is non-empty, and returns `False` otherwise.
