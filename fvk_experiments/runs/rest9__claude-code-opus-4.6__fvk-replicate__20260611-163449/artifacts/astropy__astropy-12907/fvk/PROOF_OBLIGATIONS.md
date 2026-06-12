# PROOF OBLIGATIONS: separability_matrix fix

## Bug-Fix Obligations (must change)

### PO-1: Nested right CompoundModel in `&` preserves separability

For any compound model `right` that resolves to ndarray `R` of shape (m, n), when used as the right operand of `&`, the resulting matrix must contain `R` in its lower-right block, not an all-ones submatrix.

Test: `separability_matrix(Pix2Sky_TAN() & (Linear1D(10) & Linear1D(5)))` must equal `separability_matrix(Pix2Sky_TAN() & Linear1D(10) & Linear1D(5))`

### PO-2: Deep nesting preserves separability

For arbitrarily nested `&` chains, the result must be equivalent to the flat version.

Test: `separability_matrix(Pix2Sky_TAN() & ((Linear1D(1) & Linear1D(2)) & Linear1D(3)))` must equal the flat 5-model version.

## Non-Regression Obligations (must NOT change)

### PO-3: Existing test suite passes

All 11 tests in `astropy/modeling/tests/test_separable.py` must pass unchanged.

### PO-4: Simple `&` models unchanged

`separability_matrix(Shift(1) & Shift(2))` → diagonal 2x2 (uses `_coord_matrix`, not the ndarray branch)

### PO-5: `|` (pipe) operator unchanged

`separability_matrix((Shift(1) & Shift(2)) | Rotation2D(2))` → all-True 2x2

### PO-6: Arithmetic operators unchanged

`_arith_oper` is not touched and must produce the same results.

### PO-7: `Mapping` models unchanged

`_coord_matrix` for Mapping is not touched.

### PO-8: Non-separable model coupling preserved

Models like `Rotation2D` and `Pix2Sky_TAN` must still show full input-output coupling.

### PO-9: `is_separable()` unchanged

`is_separable()` calls `_separable()` and then aggregates. Since the fix only affects the ndarray values (making them correct instead of all-ones), and `is_separable` converts via `sum(1)` and `where != 1`, the behavior is preserved for existing models and corrected for nested models.

### PO-10: Left-operand ndarray handling unchanged

The fix must not touch line 240 (`cleft[...] = left`), which is already correct.

### PO-11: `_coord_matrix` unchanged

No changes to `_coord_matrix` — it correctly handles simple Models and Mappings.

## Forbidden Changes

- Do NOT refactor `_cstack` beyond the one-line fix
- Do NOT change `_cdot`, `_arith_oper`, or `_coord_matrix`
- Do NOT add new parameters or change function signatures
- Do NOT change the `_separable` recursive dispatch logic
- Do NOT modify the `separability_matrix` or `is_separable` wrapper functions
