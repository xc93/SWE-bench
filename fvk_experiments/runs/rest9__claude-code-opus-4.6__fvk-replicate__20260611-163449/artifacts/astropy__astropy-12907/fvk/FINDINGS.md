# FINDINGS: separability_matrix nested CompoundModel bug

## Finding 1 — Asymmetric treatment of left vs right ndarray in `_cstack`

**Evidence**: `astropy/modeling/separable.py`, `_cstack` function, lines 236-246.

When the left operand is an ndarray (already-resolved compound model):
```python
cleft[: left.shape[0], : left.shape[1]] = left   # line 240 — correct, preserves matrix
```

When the right operand is an ndarray:
```python
cright[-right.shape[0]:, -right.shape[1]:] = 1    # line 245 — BUG, replaces with all-ones
```

**Input → observed vs expected**:
- Input: `separability_matrix(Pix2Sky_TAN() & (Linear1D(10) & Linear1D(5)))`
- Observed (bug): `[[T,T,F,F],[T,T,F,F],[F,F,T,T],[F,F,T,T]]` — rows 3-4 show both Linear1D outputs coupled
- Expected: `[[T,T,F,F],[T,T,F,F],[F,F,T,F],[F,F,F,T]]` — diagonal for the two independent Linear1D models

**Root cause**: The right ndarray branch uses `= 1` (scalar broadcast fills entire submatrix with True) instead of `= right` (copies the actual separability values). This was likely a typo or copy-paste error, since the left branch correctly uses `= left`.

**Classification**: Code bug — incorrect assignment in right-operand branch.

## Finding 2 — Bug only manifests with nested CompoundModels as right operand of `&`

The bug is only triggered when `right` in `_cstack` is an ndarray, which happens when the right operand of `&` is itself a CompoundModel that has already been recursively resolved by `_separable`. Simple (non-compound) right operands go through `_coord_matrix` which is correct.

This means:
- `A & B` where B is simple → correct (goes through `_coord_matrix`)
- `A & B & C` parsed as `(A & B) & C` → correct (C is simple, goes through `_coord_matrix`)
- `A & (B & C)` → **BUG** (B & C resolves to ndarray, then assigned with `= 1`)

## Finding 3 — Fix is a one-character change with no side effects

Changing `= 1` to `= right` on line 245 exactly mirrors the left-operand logic and produces the correct block-diagonal matrix. This change:
- Cannot break non-nested models (they go through `_coord_matrix`, not this branch)
- Cannot break left nesting (the left branch is already correct)
- Cannot affect `|`, `+`, `-`, `*`, `/`, `**` operators (they use `_cdot` or `_arith_oper`)
- Produces values identical to the flat (non-nested) equivalent for all tested cases

## v1 Assessment

v1 correctly identifies and fixes the single bug. The change is minimal (one token: `1` → `right`) and targets exactly the broken line. No over-generalization or collateral changes.
