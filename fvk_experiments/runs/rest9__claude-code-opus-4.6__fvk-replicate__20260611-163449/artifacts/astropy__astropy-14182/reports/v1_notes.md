# v1 Notes

## Behavioral change

v1 adds `header_rows` support to the RST writer. Before the patch, calling `tbl.write(sys.stdout, format="ascii.rst", header_rows=["name", "unit"])` raised `TypeError: RST.__init__() got an unexpected keyword argument 'header_rows'`. After the patch, it produces correct RST output with multiple header rows.

## Files modified

- `astropy/io/ascii/rst.py`: Two changes in the `RST` class:
  1. `__init__` now accepts `header_rows` parameter and forwards it to `FixedWidth.__init__`
  2. `write` method uses `len(self.header.header_rows)` to find the position line index instead of hardcoded `1`

## Public tests run

- `repo/astropy/io/ascii/tests/test_rst.py`: All 9 tests pass (no regressions)

## Why v1 matches the public issue

The issue specifically asks for `header_rows` support in RST output. The `FixedWidth` parent class already supports `header_rows`; the RST subclass just needed to accept and forward the parameter, plus fix the position line indexing in write().
