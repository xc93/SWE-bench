# SPEC: RST header_rows support

## Intended behavior change

The `RST` writer (and reader) in `astropy.io.ascii` should support the `header_rows` keyword argument, which allows multi-row headers (e.g., column name + unit) in RestructuredText simple table output.

## Format specification

For `header_rows=["name", "unit"]`, the RST output should be:

```
===== ========
 wave response
   nm       ct
===== ========
350.0      0.7
950.0      1.2
===== ========
```

Structure:
- Line 0: position line (`=` characters)
- Lines 1..N: header rows (one per entry in `header_rows`)
- Line N+1: separator line (`=` characters, identical to position line)
- Lines N+2..M: data rows
- Line M+1: closing position line (`=` characters)

## Contracts

### Write contract
- `RST.__init__(header_rows=None)` accepts an optional `header_rows` list
- Default `header_rows=None` → `["name"]` (backward compatible)
- `RST.write()` wraps the parent output with position lines at correct indices
- Position line index in the intermediate output = `len(header_rows)` (not hardcoded `1`)

### Read contract
- When `header_rows` is passed to `RST`, reading correctly parses multi-row headers
- `data.start_line` must be `len(header_rows) + 2` (position line + header rows + separator)
- `data.end_line = -1` (unchanged, skips trailing position line)

### Round-trip contract
- Writing then reading with the same `header_rows` should preserve the table data and column attributes

## Precondition
- `header_rows` must contain `"name"` (inherited from `FixedWidth`)
- Each header_row entry must correspond to a valid column attribute

## Postcondition
- Default behavior (no `header_rows` argument) is identical to the base commit
- Multi-row header output follows RST simple table format with correct separator placement
