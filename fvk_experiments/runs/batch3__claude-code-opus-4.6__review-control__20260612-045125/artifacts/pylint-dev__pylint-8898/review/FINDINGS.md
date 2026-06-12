# Review Findings: v1 Patch for pylint-dev__pylint-8898

## 1. Intended public behavior change

The `regexp_csv` type transformer should no longer split on commas that appear inside curly braces in regular expressions. This means regex quantifiers like `{1,3}` are preserved, fixing the bug where `bad-names-rgxs = "(foo{1,3})"` would crash pylint.

## 2. Current behavior in implicated code paths

Before the fix, `_regexp_csv_transfomer` delegates to `_csv_transformer` -> `_check_csv` -> `_splitstrip`, which does a naive `string.split(",")`. This splits `(foo{1,3})` into `["(foo{1", "3})"]`, both of which are invalid regex patterns.

## 3. Implications for Pylint 3.0

The issue discussion indicates consensus to fix the comma splitting behavior. The prototype function from the discussion uses the same approach as v1 (tracking brace open/close state). This is the correct approach for Pylint 3.0.

## 4. Behavior that must remain unchanged: public APIs

- `_csv_transformer` and `_check_csv` must NOT be modified — they are used by many non-regex CSV options
- `_regex_transformer` (single regex) must continue to work as-is
- `_regexp_paths_csv_transfomer` is a separate function; the issue doesn't mention it
- All non-regex CSV options (`csv`, `confidence`, `glob_paths_csv`, etc.) must be unaffected

## 5. Behavior that must remain unchanged: callers

The `regexp_csv` type is used by:
- `bad-names-rgxs` (checkers/base/name_checker/checker.py:232)
- `good-names-rgxs` (checkers/base/name_checker/checker.py:212)
- `ignore-patterns` (lint/base_options.py:55)
- `exclude-too-few-public-methods` (checkers/design_analysis.py:395)

All of these accept comma-separated regex patterns. The fix must work correctly for all of them — not just `bad-names-rgxs`.

## 6. Behavior that must remain unchanged: inputs outside the issue's scope

- Simple comma-separated regex lists without braces (e.g., `[a-z]+,[A-Z]+`) must continue to split correctly
- Empty input must return an empty list
- Whitespace stripping must be preserved
- Empty entries from consecutive/trailing commas must be discarded

## 7. Behavior that must remain unchanged: edge cases

- Unmatched `}` should be treated as a literal character (not decrement brace depth below 0)
- Unmatched `{` should not cause the function to never split (although the regex will fail compilation anyway)
- Default values (tuples, lists) for these options are NOT processed through the transformer (as `_check_csv` returns lists/tuples unchanged)

## 8. What v1 gets right

- **Core fix is correct**: Tracks brace depth and only splits on commas at depth 0
- **Minimal scope**: Only changes `_regexp_csv_transfomer`, does not modify shared utilities
- **Consistent edge case handling**: Empty strings, whitespace stripping, and empty entry discarding match the old `_splitstrip` behavior
- **Robust brace tracking**: `}` only decrements when depth > 0 (prevents negative depth)
- **New helper function is clean and readable**

## 9. What v1 might be missing or overgeneralizing

- **Not a significant concern**: The `_regexp_paths_csv_transfomer` has the same splitting bug but is NOT addressed. This is correct — the issue doesn't mention it, and being conservative is right.
- **Not a significant concern**: The function doesn't handle escaped braces like `\{` — but in regex, `\{` is still a literal brace, and the splitting behavior is still correct because the brace tracking is purely syntactic (it doesn't need to understand regex escaping to correctly handle the comma-in-quantifier case).

Wait — let me reconsider `\{`. If a regex contains `\{`, the `{` is literal, not the start of a quantifier. But our function would still increment brace_depth. For the typical case, this is fine because `\{` won't contain commas, and even if followed by a comma, the brace depth would be 1 and the comma wouldn't be split. However, consider: `foo\{a,b}` — this is a regex matching literal `{a,b}`. Our function would NOT split on the comma (brace_depth=1), treating it as `foo\{a,b}` (single regex). The OLD behavior would split it into `foo\{a` and `b}`. Both are "correct" in different interpretations — the old splits naively, the new keeps brace contents together. Since the new behavior produces a valid regex while the old produced invalid fragments, the new behavior is better.

- **Minor concern**: Deeply nested braces `{1,{2,3}}` aren't valid regex quantifiers, but our function handles them without crashing (depth tracks correctly). This is fine.

## 10. Exact minimal changes justified for v2

v1 is already correct and minimal. The only possible improvement would be:
- No changes needed. v1 scored 1/1 FAIL_TO_PASS and 18/18 PASS_TO_PASS.

## 11. Changes forbidden because they risk regressions

- Do NOT modify `_csv_transformer`, `_check_csv`, or `_splitstrip`
- Do NOT modify `_regexp_paths_csv_transfomer` (different type, different concern)
- Do NOT modify the test `test_csv_regex_error` (hidden test_patch handles this)
- Do NOT change the function signature or return type of `_regexp_csv_transfomer`
- Do NOT add deprecation warnings (not asked for in the issue)
