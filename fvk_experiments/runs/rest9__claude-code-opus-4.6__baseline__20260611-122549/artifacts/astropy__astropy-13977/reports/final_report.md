# SWE-bench Baseline: astropy__astropy-13977

## Benchmark

- Dataset: princeton-nlp/SWE-bench_Verified
- Exact row URL: https://datasets-server.huggingface.co/rows?dataset=princeton-nlp%2FSWE-bench_Verified&config=default&split=test&offset=6&length=1
- Repo: astropy/astropy
- Repo URL: https://github.com/astropy/astropy.git
- Instance ID: astropy__astropy-13977
- Base commit: 5250b2442501e6c671c6b380536f1edb352602d1
- Base commit URL: https://github.com/astropy/astropy/commit/5250b2442501e6c671c6b380536f1edb352602d1
- Version: 5.1
- Difficulty: 15 min - 1 hour

## Benchmark Discipline

- Gold patch inspected: no
- Hidden test_patch manually inspected: no
- Hidden test names inspected: no
- Hidden assertions inspected: no
- Hidden failure traces inspected: no

## Public Problem Summary

`Quantity.__array_ufunc__()` raises `ValueError` when a converter fails to handle an unrecognized input type (e.g., a duck-typed array with a `unit` attribute but not a Quantity subclass). Per numpy's `__array_ufunc__` protocol, the method should return `NotImplemented` instead, allowing the other operand's reflected method to be tried. The specific failure occurs in `_condition_arg()` which validates that values are numeric before unit conversion, but duck types produce object arrays that fail this check.

## Patch

- Files changed: `astropy/units/quantity.py`
- Behavioral change: In `Quantity.__array_ufunc__()`, the converter application loop (line 670) is wrapped in a `try/except (ValueError, TypeError)` that returns `NotImplemented` instead of propagating the exception. This allows duck-typed arrays to fall back to their own `__array_ufunc__` or reflected operators. Legitimate unit errors (`UnitsError` subclasses like `UnitConversionError`) are not affected because they are raised earlier in `converters_and_unit()`, which is not wrapped.
- Public tests run: 2570 passed across `astropy/units/tests/` (excluding pre-existing environment failures in `test_quantity_array_methods.py` and `test_quantity_non_ufuncs.py`). The specific test files `test_quantity.py` (93 passed) and `test_quantity_ufuncs.py` (201 passed) all pass.
- Why this matches the public issue statement: The issue requests that `Quantity.__array_ufunc__()` return `NotImplemented` instead of raising `ValueError` when inputs are incompatible duck types. The hint confirms this approach, suggesting a `try/except` wrapper to avoid slowing down the common case. The fix is minimal and targeted: only the converter application step is wrapped, preserving all existing error behavior for legitimate unit errors and unsupported operations.
