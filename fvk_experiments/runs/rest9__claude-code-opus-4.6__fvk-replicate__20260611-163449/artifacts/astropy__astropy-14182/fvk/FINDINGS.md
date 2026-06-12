# FINDINGS: RST header_rows support

## Finding 1 — v1 write path is correct

**Status:** Correct in v1.

The v1 patch correctly:
- Accepts `header_rows` in `RST.__init__`
- Passes it through to `FixedWidth.__init__`
- Uses dynamic `len(self.header.header_rows)` index for position line in `write()`

**Evidence:** `tbl.write(sys.stdout, format="ascii.rst", header_rows=["name", "unit"])` produces correct output:
```
===== ========
 wave response
   nm       ct
===== ========
350.0      0.7
950.0      1.2
===== ========
```

## Finding 2 — v1 read path is BROKEN for multi-row headers (CRITICAL)

**Input:** RST table with `header_rows=["name", "unit"]`:
```
===== ========
 wave response
   nm       ct
===== ========
350.0      0.7
950.0      1.2
===== ========
```

**Observed:** Reading with `header_rows=["name", "unit"]` produces corrupted data. The separator line `===== ========` at line 3 is read as a data row because `SimpleRSTData.start_line` is hardcoded to `3`.

**Expected:** Data should start at line 4 (`len(header_rows) + 2 = 4`).

**Root cause:** `SimpleRSTData` class definition hardcodes `start_line = 3`, which only works for the default single header row case. When additional header rows are present, the data start position shifts but the reader doesn't account for this.

**Fix:** In `RST.__init__`, after calling `super().__init__()`, set:
```python
self.data.start_line = len(self.header.header_rows) + 2
```

This is backward compatible: for `header_rows=["name"]`, `len + 2 = 3` (same as current hardcoded value).

## Finding 3 — No regression risk from the fix

The `data.start_line` formula `len(header_rows) + 2` produces `3` for the default case, exactly matching the current hardcoded `SimpleRSTData.start_line = 3`. All 9 existing tests remain unaffected.

## Finding 4 — `data.end_line = -1` is correct for all cases

The trailing `===` line is always the last line regardless of header row count. `end_line = -1` correctly skips it in all configurations.
