# PROOF OBLIGATIONS: RST header_rows support

## Bug obligations (FAIL_TO_PASS)

### O1: RST.__init__ accepts header_rows
- `RST(header_rows=["name", "unit"])` must not raise TypeError
- The parameter must propagate to both `self.header.header_rows` and `self.data.header_rows`

### O2: RST write with header_rows produces correct output
- Position lines (===) must appear at top, after all headers, and at bottom
- Header rows must appear in order between the top and middle position lines
- Data rows must appear between the middle and bottom position lines

### O3: RST read with header_rows parses correctly
- `data.start_line` must account for the number of header rows
- Column attributes (name, unit, etc.) must be correctly parsed from their respective header lines
- Data rows must not include the separator line

### O4: Round-trip preservation
- Write with header_rows, then read back with same header_rows, must preserve data

## Non-regression obligations (PASS_TO_PASS)

### O5: Default RST behavior unchanged
- `RST()` with no arguments must behave identically to the base commit
- `data.start_line` must equal 3 when `header_rows=["name"]` (the default)

### O6: Existing read tests unchanged
- test_read_normal: standard RST read still works
- test_read_normal_names: RST read with custom names still works
- test_read_normal_names_include: RST read with include_names still works
- test_read_normal_exclude: RST read with exclude_names still works
- test_read_unbounded_right_column: right column overflow still works
- test_read_unbounded_right_column_header: header overflow still works
- test_read_right_indented_table: indented table reading still works
- test_trailing_spaces_in_row_definition: trailing whitespace tolerance still works

### O7: Existing write test unchanged
- test_write_normal: standard RST write output format is preserved exactly

### O8: No changes to FixedWidth or other format classes
- Only rst.py should be modified
- fixedwidth.py, core.py, ui.py must remain unchanged
