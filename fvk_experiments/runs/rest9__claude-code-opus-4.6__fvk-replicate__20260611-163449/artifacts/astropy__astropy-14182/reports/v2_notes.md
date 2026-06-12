# v2 Notes

## How v2 differs from v1

v2 adds one line to `RST.__init__` after the existing `super().__init__()` call:

```python
self.data.start_line = len(self.header.header_rows) + 2
```

This dynamically sets the data start line based on the number of header rows, fixing the read path for multi-row headers.

## Which FVK findings caused the change

**Finding 2 (CRITICAL):** The read path was broken because `SimpleRSTData.start_line = 3` is hardcoded. With `header_rows=["name", "unit"]`, the RST format has:
- Line 0: position line (===)
- Line 1: name row
- Line 2: unit row
- Line 3: separator line (===)
- Line 4+: data rows

The reader was treating line 3 (separator) as data because `start_line = 3`. The fix computes `start_line = len(header_rows) + 2`, which is `4` for two header rows.

## Regression risks v2 avoids

- For default `header_rows=["name"]`: `len(["name"]) + 2 = 3`, identical to the hardcoded `SimpleRSTData.start_line = 3` — fully backward compatible
- No changes to `SimpleRSTData` class attribute (it's overridden at instance level)
- No changes to any file except `rst.py`
- All 9 existing tests pass unchanged
