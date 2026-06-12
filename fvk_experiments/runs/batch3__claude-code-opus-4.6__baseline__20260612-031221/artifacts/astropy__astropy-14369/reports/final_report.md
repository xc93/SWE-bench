# SWE-bench Baseline: astropy__astropy-14369

## Benchmark

- Dataset: princeton-nlp/SWE-bench_Verified
- Exact row URL: https://datasets-server.huggingface.co/rows?dataset=princeton-nlp%2FSWE-bench_Verified&config=default&split=test&offset=11&length=1
- Repo: astropy/astropy
- Repo URL: https://github.com/astropy/astropy.git
- Instance ID: astropy__astropy-14369
- Base commit: fa4e8d1cd279acf9b24560813c8652494ccd5922
- Base commit URL: https://github.com/astropy/astropy/commit/fa4e8d1cd279acf9b24560813c8652494ccd5922
- Version: 5.1
- Difficulty: 1-4 hours

## Benchmark Discipline

- Gold patch inspected: no
- Hidden test_patch manually inspected: no
- Hidden test names inspected: no
- Hidden assertions inspected: no
- Hidden failure traces inspected: no

## Public Problem Summary

The CDS unit format parser (`astropy/units/format/cds.py`) incorrectly handles composite units with multiple division operators. For example, `10+3J/m/s/kpc2` should parse as `1000 J / (kpc2 m s)` but instead parses as `1000 J s / (kpc2 m)`. This affects reading MRT (CDS format) files with `format='ascii.cds'`.

The root cause is that the YACC grammar for `division_of_units` uses right-recursion (`unit_expression DIVISION combined_units`), which causes `A/B/C` to parse as `A / (B / C) = A*C/B` instead of the correct left-associative `(A/B)/C = A/(B*C)`.

## Patch

- Files changed: `astropy/units/format/cds.py`, `astropy/units/format/cds_parsetab.py`
- Behavioral change: The CDS unit parser now correctly handles composite units with multiple division operators. Division is left-associative: `A/B/C` = `A / (B * C)`, matching the CDS standard where all units after `/` are in the denominator. The grammar was restructured to use left-recursive division (like the generic parser does) with product chains on the right side of each division, ensuring `.` (product) binds tighter than `/` (division) per CDS precedence rules.
- Public tests run: All 732 tests in `astropy/units/tests/test_format.py` pass (167 CDS-specific tests included).
- Why this matches the public issue statement: The fix ensures that `u.Unit('10+3J/m/s/kpc2', format='cds')` correctly produces `1000 J / (kpc2 m s)` instead of the incorrect `1000 J s / (kpc2 m)`, and similarly `10-7J/s/kpc2` correctly produces `1e-07 J / (kpc2 s)`. MRT file reading with `format='ascii.cds'` now shows correct units.
