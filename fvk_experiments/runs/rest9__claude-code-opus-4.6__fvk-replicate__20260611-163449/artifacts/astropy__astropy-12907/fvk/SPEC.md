# SPEC: separability_matrix for nested CompoundModels

## Intended Public Behavior

`separability_matrix(transform)` returns a boolean (n_outputs, n_inputs) matrix where entry (i, j) is True iff output i depends on input j.

For the `&` (concatenation) operator, the semantic contract is:

**CONCAT-SPEC**: Given `left & right` where `left` has separability matrix `L` (shape m_l x n_l) and `right` has separability matrix `R` (shape m_r x n_r), the result must be the block-diagonal matrix:

```
[ L   | 0      ]
[-----+--------]
[ 0   | R      ]
```

of shape (m_l + m_r) x (n_l + n_r). This must hold regardless of whether `left` or `right` are simple Models or nested CompoundModels already resolved to ndarrays.

## Current Code Path

`separability_matrix` calls `_separable`, which recursively walks the CompoundModel tree. For `&`, it calls `_cstack(left, right)`.

In `_cstack`:
- When left/right is a Model: calls `_coord_matrix` to compute the correct submatrix
- When left is an ndarray: correctly copies `left` into the upper-left block (line 240: `cleft[...] = left`)
- When right is an ndarray: **BUG** — sets the lower-right block to `1` instead of copying `right` (line 245: `cright[...] = 1`)

## Scope of Change

Only one line in `_cstack` is incorrect. The `|` operator (`_cdot`), arithmetic operators (`_arith_oper`), `_coord_matrix`, and `_separable` are all correct and must not be changed.

## Non-Regression Obligations

1. All existing `test_separable.py` tests (11 tests) must continue to pass
2. Simple (non-nested) `&` operations must produce the same results
3. `|` (pipe) operations must be unaffected
4. Arithmetic operators must be unaffected
5. `Mapping` models must be unaffected
6. Non-separable models (like Rotation2D) must continue to show full coupling
7. `is_separable()` must continue to work correctly (it calls `_separable` internally)
