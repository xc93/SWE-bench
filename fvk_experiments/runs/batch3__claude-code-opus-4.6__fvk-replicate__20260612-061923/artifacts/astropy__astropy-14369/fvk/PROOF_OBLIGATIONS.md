# Proof Obligations

## Bug-revealing obligations (FAIL_TO_PASS)

1. **O-F1:** `CDS.parse('10+3J/m/s/kpc2')` must return a unit equivalent to `1000 * J / (kpc^2 * m * s)`
2. **O-F2:** `CDS.parse('10-7J/s/kpc2')` must return a unit equivalent to `1e-7 * J / (kpc^2 * s)`
3. **O-F3:** Unknown — possibly MRT table reading, or a `to_string` round-trip, or a direct grammar test

## Non-regression obligations (PASS_TO_PASS)

These must ALL remain satisfied:

### Parser correctness (existing test_format.py parametrized cases)
4. **O-P1:** Single-slash units parse correctly: `km/s`, `°/s`, `Å/s`, `[cm/s2]`
5. **O-P2:** Products parse correctly: `m.s`, `J.m`
6. **O-P3:** Factor+unit: `10+3`, `10-7`, `2x10-9`
7. **O-P4:** Dimensionless: `---`, `-`
8. **O-P5:** Power notation: `m2`, `kpc-2`, `s-1`
9. **O-P6:** Dex/bracket notation: `[cm/s2]`, `[K]`, `[-]`

### IO correctness (existing test_cds.py)
10. **O-P7:** MRT table round-trip: read → write → compare
11. **O-P8:** Unit display in table: column units match CDS format
12. **O-P9:** Null handling: `---` units produce `None`

### Format correctness
13. **O-P10:** `CDS.to_string()` produces valid parseable CDS strings
14. **O-P11:** Round-trip: `CDS.parse(CDS.to_string(unit)) == unit`

## Key risks for v2

- Modifying the PLY grammar risks LALR conflict resolution changes → regressions
- Modifying `to_string` risks breaking existing round-trip tests
- Modifying the parse table (`cds_parsetab.py`) must be consistent with the grammar

## Minimal change principle

The safest v2:
1. Keep the preprocessing fix in `CDS.parse()` (preserves all PASS_TO_PASS)
2. If modifying `to_string`, ensure existing format tests still pass
3. Do NOT change the PLY grammar (learned from the regression at 731/732)
