# ITERATION GUIDANCE: v1 → v2

## What v1 got right
1. Accepting `header_rows` parameter in `RST.__init__`
2. Forwarding it to `FixedWidth.__init__` via `super().__init__()`
3. Dynamic position line indexing in `write()` using `len(self.header.header_rows)`

## What v1 is missing
1. **CRITICAL:** `data.start_line` is not adjusted for multi-row headers in the read path. `SimpleRSTData` hardcodes `start_line = 3`, which only works for single header row. With N header rows, data starts at line `N + 2`.

## Exact change for v2

In `RST.__init__`, after the existing `super().__init__()` call, add one line:

```python
self.data.start_line = len(self.header.header_rows) + 2
```

This overrides the hardcoded `SimpleRSTData.start_line = 3` with a dynamic value.

## Backward compatibility verification
- `header_rows=None` → defaults to `["name"]` → `len + 2 = 3` (unchanged from base)
- `header_rows=["name"]` → `len + 2 = 3` (unchanged from base)
- `header_rows=["name", "unit"]` → `len + 2 = 4` (correct for 2-row headers)

## Forbidden changes
- Do NOT modify `SimpleRSTData.start_line` class attribute (it's a class-level default)
- Do NOT modify `SimpleRSTData.end_line` (already correct at `-1`)
- Do NOT modify `SimpleRSTHeader.position_line` or `SimpleRSTHeader.start_line`
- Do NOT modify any file other than `astropy/io/ascii/rst.py`
- Do NOT add/remove/change methods beyond `RST.__init__` and `RST.write`
