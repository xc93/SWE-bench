# SWE-bench Baseline: pylint-dev__pylint-8898

## Benchmark

- Dataset: princeton-nlp/SWE-bench_Verified
- Exact row URL: https://datasets-server.huggingface.co/rows?dataset=princeton-nlp%2FSWE-bench_Verified&config=default&split=test&offset=329&length=1
- Repo: pylint-dev/pylint
- Repo URL: https://github.com/pylint-dev/pylint.git
- Instance ID: pylint-dev__pylint-8898
- Base commit: 1f8c4d9eb185c16a2c1d881c054f015e1c2eb334
- Base commit URL: https://github.com/pylint-dev/pylint/commit/1f8c4d9eb185c16a2c1d881c054f015e1c2eb334
- Version: 3.0
- Difficulty: 1-4 hours

## Benchmark Discipline

- Gold patch inspected: no
- Hidden test_patch manually inspected: no
- Hidden test names inspected: no
- Hidden assertions inspected: no
- Hidden failure traces inspected: no

## Public Problem Summary

The `bad-names-rgxs` option (and other options using `regexp_csv` type) splits values on commas to support comma-separated lists of regular expressions. However, this naive splitting mangles regex patterns that contain commas inside curly brace quantifiers (e.g., `{1,3}`). The pattern `(foo{1,3})` gets split into `(foo{1` and `3})`, causing a crash because both fragments are invalid regex.

## Patch

- Files changed: `pylint/config/argument.py`, `tests/config/test_config.py`
- Behavioral change: Added `_split_csv_regex()` function that splits on commas only when they are not inside curly braces `{}`. Both `_regexp_csv_transfomer` and `_regexp_paths_csv_transfomer` now use this function instead of `_csv_transformer`. Updated existing test `test_csv_regex_error` to use a genuinely invalid regex pattern instead of one that was only broken due to the bug.
- Public tests run: `tests/config/test_config.py` (16 passed), `tests/checkers/base/` (8 passed, 1 skipped)
- Why this matches the public issue statement: The issue reports that commas in regex quantifiers like `{1,3}` cause the regex to be mangled. The fix preserves commas inside curly braces during splitting, allowing valid regex patterns with quantifiers to work correctly.
