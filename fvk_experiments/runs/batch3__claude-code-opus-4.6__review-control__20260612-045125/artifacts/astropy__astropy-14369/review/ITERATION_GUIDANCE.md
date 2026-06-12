# Iteration Guidance for v2

## Problem Diagnosis

v1 scores 2/3 FAIL_TO_PASS, 731/732 PASS_TO_PASS. Two issues:
1. **1 PASS_TO_PASS regression**: Most likely caused by including the auto-generated `cds_parsetab.py` in the patch. This file contains PLY parser tables that are environment-dependent (PLY version, Python version, line numbers). If it fails to apply cleanly or applies with corruption, the parser may malfunction.
2. **1 missing FAIL_TO_PASS**: The grammar fix is correct for the reported bug. If a hidden test still fails, it might be testing a pattern or behavior not covered by the grammar change alone.

## v2 Strategy

### Change 1: Remove `cds_parsetab.py` from the patch (HIGH CONFIDENCE)

- Reset `cds_parsetab.py` to the original base commit version
- The patch should ONLY modify `cds.py`
- PLY will detect the grammar signature mismatch at import time and regenerate the parser table in memory
- This is the standard PLY behavior and is safe
- This should fix the 1 PASS_TO_PASS regression

### Change 2: Keep the grammar fix in `cds.py` (HIGH CONFIDENCE)

The grammar restructure is correct:
- `combined_units` handles division with left-recursion (left-associative)
- `product_of_units` chains only products (`.` has higher precedence than `/`)
- Prefix division (`DIVISION product_of_units`) preserved

### Validation Plan

1. Run all test_format.py tests (732 expected pass)
2. Run all test_cds.py tests (12 expected pass)
3. Run test_cds_header_from_readme.py tests
4. Verify the bug fix for both example unit strings
5. Verify single-slash, product, parenthesized, and prefix division patterns

### What NOT to change

- Do not modify `to_string` or any other format method
- Do not modify the CDS I/O reader
- Do not add error handling or validation
- Do not touch any other parser files
- Keep the grammar change minimal and identical to v1's `cds.py` change
