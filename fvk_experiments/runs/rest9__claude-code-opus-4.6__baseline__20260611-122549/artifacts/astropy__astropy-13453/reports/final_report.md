# SWE-bench Baseline: astropy__astropy-13453

## Benchmark

- Dataset: princeton-nlp/SWE-bench_Verified
- Exact row URL: https://datasets-server.huggingface.co/rows?dataset=princeton-nlp%2FSWE-bench_Verified&config=default&split=test&offset=4&length=1
- Repo: astropy/astropy
- Repo URL: https://github.com/astropy/astropy.git
- Instance ID: astropy__astropy-13453
- Base commit: 19cc80471739bcb67b7e8099246b391c355023ee
- Base commit URL: https://github.com/astropy/astropy/commit/19cc80471739bcb67b7e8099246b391c355023ee
- Version: 5.0
- Difficulty: 15 min - 1 hour

## Benchmark Discipline

- Gold patch inspected: no
- Hidden test_patch manually inspected: no
- Hidden test names inspected: no
- Hidden assertions inspected: no
- Hidden failure traces inspected: no

## Public Problem Summary

When writing an astropy Table to HTML format using `table.write(sp, format="html", formats={"a": ".2e"})`, the `formats` keyword argument is silently ignored. The same `formats` argument works correctly for other output formats like CSV and RST. The root cause is that the `HTML.write()` method in `astropy/io/ascii/html.py` calls `self.data._set_fill_values(cols)` but never calls `self.data._set_col_formats()`, so column format specifications are never applied before string conversion.

## Patch

- Files changed: `astropy/io/ascii/html.py`
- Behavioral change: After setting fill values on columns, the HTML writer now also sets `self.data.cols = cols` and calls `self.data._set_col_formats()`, which applies any user-supplied `formats` to the columns before their values are converted to strings. This mirrors the behavior in `BaseData.str_vals()` used by other writers.
- Public tests run: `astropy/io/ascii/tests/test_html.py` — 9 passed, 16 skipped (bs4 not installed)
- Why this matches the public issue statement: The issue reports that `formats={"a": lambda x: f"{x:.2e}"}` is ignored when writing HTML. The fix ensures that `_set_col_formats()` is called in the HTML write path, which applies the formats before `iter_str_vals()` generates the output strings. Verified with the exact reproducer from the issue — output now shows `1.24e-24` instead of `1.23875234858e-24`.
