# Iteration Guidance for v2

## Summary of v1 performance

- FAIL_TO_PASS: 2/3 (misses one test)
- PASS_TO_PASS: 732/732 (no regressions)
- v1 approach: preprocessing in CDS.parse() to convert `a/b/c` → `a/b.c`

## What v1 does right

1. Correctly fixes the CDS unit parsing for multiple slashes
2. Handles parenthesized expressions correctly (paren-depth tracking)
3. Preserves all 732 regression tests
4. Preserves single-slash behavior
5. Preserves product notation behavior
6. The preprocessing is in CDS.parse(), which all public API paths use

## What v1 might be missing

The 3rd FAIL_TO_PASS test still fails. Possible explanations (in decreasing likelihood):

### Hypothesis A: The grammar-level fix is also needed
The test might call the parser grammar directly or through a path that bypasses `CDS.parse()`. However, modifying the grammar to left-recursive caused a PASS_TO_PASS regression.

**Action for v2:** Try a more conservative grammar change that only modifies the division rule's action, not the grammar structure. For example, keep the right-recursive grammar but intercept the division result.

### Hypothesis B: to_string needs to produce slash notation
The `to_string` method currently produces `J.m-1.s-1` instead of `J/m.s`. If a test checks `to_string` output for CDS format, it might expect slash notation.

**Action for v2:** Modify `_format_unit_list` or `to_string` to produce slash-separated output. But ONLY if it doesn't break existing tests.

### Hypothesis C: Additional CDS format parsing edge case
There might be a specific unit string pattern that the preprocessing doesn't handle.

**Action for v2:** Test more edge cases, especially those involving powers, factors, and parentheses with multiple slashes.

## Recommended v2 approach

**Priority 1:** Keep the preprocessing fix (proven safe, 732/732 PASS_TO_PASS).

**Priority 2:** Try modifying `to_string` to use slash notation. Test against existing 732 tests first. If it passes, include it.

**Priority 3:** If Priority 2 doesn't work, try a minimal grammar fix (only `p_division_of_units`) that doesn't change the product rule.

## What NOT to do in v2

1. Do NOT change `product_of_units` from right-recursive to left-recursive (caused regression)
2. Do NOT remove the preprocessing fix (it's proven safe)
3. Do NOT change unrelated code
4. Do NOT modify test files
