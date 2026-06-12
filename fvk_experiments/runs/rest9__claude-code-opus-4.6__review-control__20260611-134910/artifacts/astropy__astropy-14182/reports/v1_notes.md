# v1 Notes

## Behavioral change

v1 adds support for the `header_rows` parameter in the RST reader/writer. Three changes:

1. `RST.__init__()` now accepts `header_rows` and passes it to `FixedWidth.__init__()`.
2. `RST.__init__()` sets `self.data.start_line = len(self.header.header_rows) + 2` so the reader correctly skips multi-row headers (position_line + N header rows + second position_line = N+2).
3. `RST.write()` uses `len(self.header.header_rows)` instead of hardcoded `1` to find the position line index, so multi-row headers are correctly wrapped with `=` separators.

## Files modified

- `astropy/io/ascii/rst.py`: changes in `RST.__init__()` and `RST.write()`

## Public tests run

- `repo/astropy/io/ascii/tests/test_rst.py`: 9/9 passed
- Manual verification of roundtrip read/write with `header_rows=["name", "unit"]`

## Why v1 matches the issue

The issue requests that `tbl.write(sys.stdout, format="ascii.rst", header_rows=["name", "unit"])` work instead of raising TypeError. The fix enables both writing and reading RST tables with custom header_rows. Default behavior (no `header_rows` argument) is preserved since `header_rows=None` defaults to `["name"]` in `FixedWidth.__init__()`, and `data.start_line` computes to `1 + 2 = 3` matching the original class attribute.
