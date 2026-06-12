# v1 Notes

## What behavior v1 changes

The CDS unit parser (`astropy/units/format/cds.py`) incorrectly handles unit strings with multiple slashes. For example:

- `10+3J/m/s/kpc2` was parsed as `1000 J s / (kpc2 m)` (wrong: `s` in numerator)
- `10-7J/s/kpc2` was parsed as `1e-07 J kpc2 / s` (wrong: `kpc2` in numerator)

The correct results should be:
- `1000 J / (kpc2 m s)`
- `1e-07 J / (kpc2 s)`

The root cause is the right-recursive grammar rule for `division_of_units`, which makes `a/b/c` parse as `a/(b/c) = a*c/b` instead of the intended `a/(b*c)`.

v1 fixes this with two changes:

1. **Grammar fix**: Changed the PLY grammar to make division left-associative. Replaced the right-recursive `division_of_units` non-terminal with a left-recursive rule in `combined_units`. Also made `product_of_units` left-recursive for consistency.

2. **Preprocessing fix**: Added string preprocessing in `CDS.parse()` that transforms multiple slashes into a single slash with products in the denominator: `a/b/c/d` becomes `a/b.c.d`. Respects parenthesis nesting.

## Files modified

- `repo/astropy/units/format/cds.py` — grammar rewrite + preprocessing in `parse()`
- `repo/astropy/units/format/cds_parsetab.py` — regenerated PLY parse table

## Public tests run

- `pytest repo/astropy/units/tests/test_format.py` — 732/732 passed
- `pytest repo/astropy/io/ascii/tests/test_cds.py` — 12/12 passed
- Manual verification of the exact issue examples from the bug report
- Direct parser tests (bypassing `CDS.parse()`) verified correct behavior

## Why v1 matches the public issue

The issue reports that reading MRT files with composite CDS units like `10+3J/m/s/kpc2` produces incorrect unit parsing. The fix ensures that multiple slashes in CDS unit strings are correctly interpreted at the grammar level: division is left-associative, so `a/b/c = (a/b)/c = a/(b*c)`.
