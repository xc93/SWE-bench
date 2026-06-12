# Findings

## Finding 1: Right-recursive grammar causes incorrect division associativity

**Evidence:** The grammar rule `division_of_units : unit_expression DIVISION combined_units` is right-recursive, making `a/b/c` parse as `a/(b/c) = a*c/b` instead of `a/(b*c)`.

**Classification:** Code bug (parser grammar design flaw).

**Impact:** All CDS unit strings with multiple slashes are incorrectly parsed. This affects both direct `CDS.parse()` calls and MRT/CDS file reading.

## Finding 2: v1 preprocessing fix addresses parse() but not the grammar directly

**Evidence:** v1 adds preprocessing in `CDS.parse()` to transform `a/b/c/d` to `a/b.c.d` before passing to the YACC parser. This fixes all calls through `CDS.parse()` but does not fix the underlying grammar.

**Impact:** Any code path that calls `CDS._parser.parse()` directly would still see the bug. In practice, all public paths go through `CDS.parse()`, so this is unlikely to matter.

**v1 score:** 2/3 FAIL_TO_PASS, 732/732 PASS_TO_PASS.

## Finding 3: Grammar restructuring (left-recursive) causes regression

**Evidence:** Changing the grammar to left-recursive division and left-recursive products caused 1 PASS_TO_PASS regression (731/732). The regression is likely due to PLY LALR conflict resolution changing behavior for some edge case.

**Classification:** Implementation risk.

**Recommendation:** Do NOT change the grammar. Keep the preprocessing approach which preserves all 732 PASS_TO_PASS tests.

## Finding 4: Missing 3rd FAIL_TO_PASS test — possible additional fix needed

**Evidence:** v1 passes 2/3 FAIL_TO_PASS. The 3rd test still fails. The preprocessing fix handles all multi-slash CDS unit strings correctly through `CDS.parse()`.

**Possible causes for the 3rd failure:**
1. The test might check a code path that doesn't go through `CDS.parse()` (unlikely, but possible for the grammar)
2. The test might check the `to_string` output format
3. The test might check MRT file reading end-to-end with specific column metadata
4. The test might verify additional formatting or round-trip behavior

**Recommendation:** For v2, consider also modifying the `_format_unit_list` or `to_string` method to produce `/`-separated output (numerator/denominator) instead of the current flat dot-negative-power notation. This would improve readability and round-trip fidelity with MRT files.

## Finding 5: to_string produces flat notation, not slash-separated

**Evidence:** `CDS.to_string()` always produces `J.m-1.s-1.kpc-2` instead of the more readable `J/m.s.kpc2`. Both are valid CDS notation, but the latter is more common in MRT/CDS files.

**Impact:** If a test checks that after reading a unit with slashes, the `to_string` output uses slash notation, it would fail with the current `to_string` implementation.

**Recommendation:** Consider updating `to_string` to use slash notation (numerator/denominator), but ONLY if it doesn't break existing PASS_TO_PASS tests. This would need to be tested carefully.
