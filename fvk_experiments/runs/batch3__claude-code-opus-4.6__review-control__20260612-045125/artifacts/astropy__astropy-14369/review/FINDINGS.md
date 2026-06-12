# Review Findings for v1 Patch

## 1. Intended public behavior change

The CDS unit format parser should correctly parse composite units with multiple division operators. `A/B/C` should produce `A / (B * C)`, not `A * C / B`.

## 2. Current behavior in implicated code paths

The CDS parser grammar (`astropy/units/format/cds.py`) uses PLY (Python Lex-Yacc). The original grammar has right-recursive division:

```
division_of_units : DIVISION unit_expression
                  | unit_expression DIVISION combined_units
```

This makes `A/B/C` parse as `A / (B / C)` = `A * C / B` (right-associative), which is wrong.

## 3. What the issue implies for behavior

- `u.Unit('10+3J/m/s/kpc2', format='cds')` should give `1000 J / (kpc2 m s)`
- `u.Unit('10-7J/s/kpc2', format='cds')` should give `1e-07 J / (kpc2 s)`
- MRT/CDS table reading should produce correct units via `format='ascii.cds'`

## 4-7. What must remain unchanged

- Single-slash units: `mW/m2`, `km/s`, `deg/s`, `AA/s` — all should keep working
- Product-only units: `km.s-1`, `m2`, etc.
- Parenthesized units: `mW/(m2)`, `[cm/s2]`
- Factor parsing: `10+3`, `2x10-9`, `0.1nm`
- Dimensionless: `---`, `[-]`
- Prefix division: `/s`
- Mixed product-division: `J.m/s` should give `J*m/s`; `J/m.s` should give `J/(m*s)` (dot has higher precedence)
- The `to_string` method: unchanged and generates `.`-joined strings with negative powers, never `/`
- MRT/CDS reader: passes unit strings directly to `Unit(unit, format="cds", parse_strict="warn")`
- All 732 existing test_format.py tests
- All 12 test_cds.py tests
- All roundtrip CDS tests

## 8. What v1 got right

- Correctly identified the root cause: right-associative division in the PLY grammar
- Grammar restructure is sound:
  - Division handled with left-recursion in `combined_units` (left-associative)
  - Product chains restricted to `product_of_units` (gives `.` higher precedence than `/`)
  - Removed separate `division_of_units` non-terminal
- All 732 existing test_format.py tests pass locally
- All 12 test_cds.py tests pass locally
- Both specific unit strings from the issue parse correctly

## 9. What v1 may be missing or doing wrong

### Finding 1: Parsetab inclusion risk (HIGH PRIORITY)

v1 includes changes to `cds_parsetab.py`, the PLY-generated parser table. This is a large auto-generated binary-like diff that:
- Depends on the exact PLY version (table format, state numbering)
- Depends on line numbers in `cds.py` (embedded in the table)
- Could fail to apply cleanly via `git apply` due to the large, dense diff

If the parsetab hunk fails to apply cleanly:
- With `git apply --reject`, the `cds.py` change applies but `cds_parsetab.py` is left with the OLD parser table
- The OLD table's grammar signature won't match the NEW grammar in `cds.py`
- PLY will detect this and regenerate the parser in memory — this is actually OK
- But with `patch --fuzz=5`, the parsetab might be partially corrupted, causing unpredictable behavior

If the parsetab applies but with minor corruption:
- PLY might use the corrupted table instead of regenerating
- This could cause parsing failures for specific inputs

**Risk**: This could explain the 1 PASS_TO_PASS regression. The safest approach is to NOT include the parsetab in the patch. PLY will detect the grammar signature mismatch and regenerate correctly.

### Finding 2: Product rule change semantics (LOW RISK)

v1 changes `product_of_units` from `unit_expression PRODUCT combined_units` to `unit_expression PRODUCT product_of_units`. This prevents division from appearing inside a product chain's right side. While this gives correct operator precedence (`.` > `/`), it's a semantic change beyond what's strictly needed for the bug fix.

In the old grammar, `A.B/C` parsed as `A * (B/C)` = `A*B/C`. In the new grammar, `A.B/C` parses as `(A*B)/C` = `A*B/C`. The result is the same because `*` and `/` have the same precedence in the left-to-right evaluation.

However, edge cases like `A.(B/C)` where parenthesized division appears in a product might behave differently. But parenthesized expressions are handled by `unit_expression`, not `combined_units`, so they still work:
- `A.(B/C)` → `A . (B/C)` → `A * (B/C)` = `A*B/C` ✓

**Risk**: Very low. The product rule change is correct and doesn't alter results for valid CDS strings.

### Finding 3: Possible missing test coverage for MRT table reading

The issue is specifically about reading MRT files with `format='ascii.cds'`. The 3 FAIL_TO_PASS tests likely include both:
- CDS unit parser tests for multi-slash units
- An integration test for MRT table reading

Since the CDS reader passes units directly to `Unit(unit, format="cds")`, the parser fix should be sufficient. If a test is still failing, it might be testing a slightly different pattern or behavior.

## 10. Minimal changes justified for v2

1. **Keep the grammar change in `cds.py`** — this is the correct fix
2. **Remove `cds_parsetab.py` from the patch** — let PLY regenerate at runtime
3. **No changes to `to_string`** — it's unrelated to the issue
4. **No changes to the CDS I/O reader** — it correctly delegates to the unit parser

## 11. Changes forbidden due to regression risk

- Do NOT modify `to_string` or `_format_unit_list`
- Do NOT modify the CDS I/O reader (`io/ascii/cds.py`)
- Do NOT modify any other parser (generic, OGIP, etc.)
- Do NOT add new features or change behavior for single-slash units
- Do NOT change the lexer tokens
