# SWE-bench Baseline: astropy__astropy-14182

## Benchmark

- Dataset: princeton-nlp/SWE-bench_Verified
- Exact row URL: https://datasets-server.huggingface.co/rows?dataset=princeton-nlp%2FSWE-bench_Verified&config=default&split=test&offset=8&length=1
- Repo: astropy/astropy
- Repo URL: https://github.com/astropy/astropy.git
- Instance ID: astropy__astropy-14182
- Base commit: a5917978be39d13cd90b517e1de4e7a539ffaa48
- Base commit URL: https://github.com/astropy/astropy/commit/a5917978be39d13cd90b517e1de4e7a539ffaa48
- Version: 5.1
- Difficulty: 15 min - 1 hour

## Benchmark Discipline

- Gold patch inspected: no
- Hidden test_patch manually inspected: no
- Hidden test names inspected: no
- Hidden assertions inspected: no
- Hidden failure traces inspected: no

## Public Problem Summary

The RST (reStructuredText) ASCII table writer in astropy does not support the `header_rows` parameter. When calling `tbl.write(sys.stdout, format="ascii.rst", header_rows=["name", "unit"])`, a `TypeError` is raised because `RST.__init__()` does not accept `header_rows`. The FixedWidth writer (RST's parent class) already supports `header_rows`, so RST just needs to accept and forward the parameter.

## Patch

- Files changed: `astropy/io/ascii/rst.py`
- Behavioral change:
  - `RST.__init__()` now accepts an optional `header_rows` parameter and forwards it to the parent `FixedWidth.__init__()`.
  - `RST.write()` dynamically determines the position line index based on the number of header rows (was hardcoded to index 1, now uses `len(self.data.header_rows)`).
  - `self.data.start_line` is set to `len(header_rows) + 2` to correctly handle reading RST tables with multiple header rows (accounts for the top border line, header rows, and separator line).
- Public tests run: All 9 existing tests in `test_rst.py` pass (PASS_TO_PASS: 9/9).
- Why this matches the public issue statement: The issue requests that `header_rows` be supported in RST output. The patch enables exactly that by forwarding the parameter to the parent class that already implements the feature, and adjusting the RST-specific border line logic to handle multiple header rows.
