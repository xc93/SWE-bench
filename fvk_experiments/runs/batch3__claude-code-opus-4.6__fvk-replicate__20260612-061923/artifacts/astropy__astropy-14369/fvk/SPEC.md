# Formal Specification: CDS Unit Parser Multiple Slash Fix

## Intended Behavior (from public issue)

The CDS unit parser (`astropy/units/format/cds.py`) should parse composite unit strings with multiple `/` (division) operators according to the CDS standard, where everything after the first `/` is in the denominator.

### Specification of `CDS.parse(s)`

**Precondition:** `s` is a valid CDS unit string (no whitespace).

**Postcondition for multiple slashes:**
For any CDS unit string `A/B/C/D/...`, the result should be `A / (B * C * D * ...)`. That is, `/` acts as a separator between numerator and denominator, and subsequent `/` operators are treated as products in the denominator.

Equivalently:
- `a/b/c` = `a / (b * c)` (NOT `a / (b / c) = a * c / b`)
- Division is effectively left-associative: `(a / b) / c = a / (b * c)`

### Current (buggy) behavior

The grammar uses right-recursive division:
```
division_of_units : unit_expression DIVISION combined_units
```

This makes `a/b/c` parse as `a / (b / c) = a * c / b`, which is incorrect.

### Examples

| Input                | Expected                    | Current (bug)               |
|---------------------|----------------------------|-----------------------------|
| `10+3J/m/s/kpc2`   | `1000 J / (kpc2 m s)`     | `1000 J s / (kpc2 m)`     |
| `10-7J/s/kpc2`     | `1e-07 J / (kpc2 s)`      | `1e-07 J kpc2 / s`        |
| `J/m/s`            | `J / (m s)`                | `J s / m`                  |

## What must remain unchanged

1. Single-slash parsing: `J/m`, `km/s`, `cm/s2` must not change behavior.
2. Product parsing: `J.m`, `km.s` must not change behavior.
3. Mixed product/slash: `J.m/s.kpc2` = `J * m / (s * kpc2)` must not change.
4. Factor parsing: `10+3`, `10-7`, `2x10-9` must not change.
5. Bracket/dex notation: `[cm/s2]`, `[-]` must not change.
6. Dimensionless: `---`, `-` must not change.
7. Parenthesized expressions: `(J/m)` must not change.
8. The `to_string()` method must not change output format.
9. All 732 existing PASS_TO_PASS tests must continue to pass.
10. The PLY parser table (`cds_parsetab.py`) should not need changes for maximum compatibility.
