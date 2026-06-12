# SPEC — pylint-dev__pylint-8898

## Intended Behavior Change

The `_regexp_csv_transfomer` function should split a comma-separated string of regular expressions into individual regex patterns **without** splitting on commas that are inside curly braces (regex quantifiers like `{1,3}`).

### Precondition

- `value` is a string (possibly empty) containing one or more regex patterns separated by commas.
- Commas inside `{...}` are part of regex quantifier syntax, not separators.

### Postcondition

- Returns a list of compiled `re.Pattern` objects.
- Each regex in the input is compiled individually.
- Commas outside `{...}` are treated as separators.
- Commas inside `{...}` are preserved within the regex pattern.
- Empty/whitespace-only segments between commas are discarded.
- Leading/trailing whitespace around each pattern is stripped.
- Invalid regex patterns raise `argparse.ArgumentTypeError` with a clear message.

### Invariant

- The behavior of `_csv_transformer`, `_check_csv`, `_splitstrip`, and all other type transformers remains unchanged.
- The behavior of `_regexp_paths_csv_transfomer` is NOT changed (it uses `_csv_transformer` and path patterns typically don't contain regex quantifiers).
- The behavior of `_regex_transformer` (single regex) is unchanged.

## Scope of Change

Only `_regexp_csv_transfomer` in `pylint/config/argument.py` is affected. All four options using `regexp_csv` type benefit:

1. `ignore-patterns` (in `pylint/lint/base_options.py`)
2. `good-names-rgxs` (in `pylint/checkers/base/name_checker/checker.py`)
3. `bad-names-rgxs` (in `pylint/checkers/base/name_checker/checker.py`)
4. `exclude-too-few-public-methods` (in `pylint/checkers/design_analysis.py`)

## What Must NOT Change

1. Simple comma-separated lists without braces: `"a,b,c"` -> `["a", "b", "c"]`
2. Single regex without commas: `"foo"` -> `["foo"]`
3. Empty string: `""` -> `[]`
4. Whitespace handling (strip around patterns)
5. Error handling for invalid regex patterns
6. All other option type transformers
7. `_regexp_paths_csv_transfomer` behavior
