# Review Findings: v1 Patch for astropy__astropy-14182

## 1. Intended public behavior change

The public issue requests that `tbl.write(sys.stdout, format="ascii.rst", header_rows=["name", "unit"])` produce an RST table with multiple header rows (name and unit) instead of raising `TypeError`. The `ascii.fixed_width` format already supports `header_rows`; the issue asks for parity in `ascii.rst`.

## 2. Current behavior in implicated code paths

Before the patch, `RST.__init__()` accepts no arguments (besides `self`). Any kwargs like `header_rows` passed via `_get_writer` in `core.py` raise `TypeError`. The `write()` method hardcodes `lines[1]` as the position line index, which only works for exactly one header row.

## 3. What the issue implies for astropy versions

The issue was filed against astropy 5.1. It requests a new feature (multi-header RST output), not a bug fix. The fix should add functionality without altering existing behavior.

## 4. Behavior that must remain unchanged for touched public APIs

- Default RST writing (no `header_rows` arg): output must be identical to pre-patch.
- Default RST reading: all 9 existing tests must pass.
- The `FixedWidth` class hierarchy behavior is not touched and must be unaffected.

## 5. Behavior that must remain unchanged for related code paths

- `FixedWidth.__init__` behavior unchanged (RST only adds `header_rows` forwarding).
- `FixedWidthData.write()` logic unchanged.
- `FixedWidthHeader.process_val()` logic unchanged.
- `_get_writer()` in `core.py` unchanged - `header_rows` correctly passes through since it's not in `extra_writer_pars`.

## 6. Behavior for inputs outside the issue's scope

- RST tables without `header_rows` must produce identical output.
- RST read of standard single-header tables must work identically.
- Other formats (`fixed_width`, `fixed_width_two_line`, etc.) must be unaffected.

## 7. Edge cases, error handling, metadata

- Empty `header_rows=[]`: pathological, would cause double-separator at start of write output. Not requested by the issue, and consistent with how `FixedWidth` handles it.
- `header_rows` with non-existent column attributes: would produce empty strings. Same behavior as `FixedWidth`.
- Comment lines and blank lines in RST read: handled by `process_lines()`, unaffected by the patch.

## 8. What v1 got right

1. **Accepts `header_rows` correctly**: Forwards to `FixedWidth.__init__()`, which handles defaulting to `["name"]`.
2. **Fixes write position line index**: Uses `len(self.header.header_rows)` instead of hardcoded `1`. For default case, `len(["name"]) = 1`, preserving existing behavior.
3. **Fixes read data start line**: Sets `self.data.start_line = len(self.header.header_rows) + 2`. For default case, `1 + 2 = 3`, matching `SimpleRSTData.start_line = 3`.
4. **Pattern consistent with codebase**: `FixedWidthTwoLine.__init__` also overrides `data.start_line` after calling `super().__init__()` (line 490 of fixedwidth.py).
5. **Minimal change**: Only 4 lines changed in a single file.

## 9. What v1 is missing or overgeneralizing

**Nothing identified.** The patch is minimal and correctly scoped:
- It doesn't touch files outside `rst.py`.
- It doesn't change the class hierarchy.
- It doesn't alter default behavior.
- The `data.start_line` formula is correct: RST format has `position_line(=) + N headers + position_line(=)` before data, so `data.start_line = N + 2`.
- The `write()` position line index is correct: in `FixedWidthData.write()` output, position line follows all header rows, so it's at index `N`.

## 10. Minimal changes justified for v2

**No changes needed.** v1 is already correct and minimal. The patch:
- Solves the issue (write with header_rows works).
- Enables reading RST tables with header_rows.
- Preserves all existing behavior.
- Passes all 9 existing tests.
- Passes the hidden test (1/1 FAIL_TO_PASS).

## 11. Changes forbidden because they risk regressions

- Do not change `SimpleRSTHeader.position_line`, `SimpleRSTHeader.start_line`, or `SimpleRSTData.end_line` class attributes.
- Do not modify `FixedWidthData.write()` or `FixedWidthHeader.process_val()`.
- Do not add parameters beyond `header_rows` to `RST.__init__()`.
- Do not change `delimiter_pad=None` or `bookend=False` defaults.
