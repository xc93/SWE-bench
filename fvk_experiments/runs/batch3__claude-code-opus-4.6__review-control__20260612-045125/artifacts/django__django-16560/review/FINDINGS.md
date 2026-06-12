# Review Findings for v1 Patch

## 1. Intended public behavior change
Add a `violation_error_code` parameter to `BaseConstraint` and its subclasses (`CheckConstraint`, `UniqueConstraint`, `ExclusionConstraint`) so the `code` attribute of `ValidationError` raised by `validate()` can be customized without subclassing.

## 2. Current behavior in implicated code paths
- `BaseConstraint` has `violation_error_message` but no `violation_error_code`.
- `CheckConstraint.validate()`, `UniqueConstraint.validate()`, and `ExclusionConstraint.validate()` raise `ValidationError(message)` with no explicit `code=` argument, resulting in `code=None` on the error.

## 3. Implications for Django 5.0/5.1/future
- The new parameter must be keyword-only, following the same pattern as `violation_error_message`.
- Backward compatibility: default `None` means no code is passed, preserving existing behavior.

## 4-7. What must remain unchanged
- All existing constraint creation, deconstruction, equality, repr behavior when `violation_error_code` is not specified.
- The backward-compatible `unique_error_message()` path in `UniqueConstraint.validate()` for field-based constraints.
- The deprecated positional arguments path in `BaseConstraint.__init__`.
- All 66 regression tests must continue to pass.

## 8. What v1 got right
- Added `violation_error_code` to `BaseConstraint.__init__`, `CheckConstraint.__init__`, `UniqueConstraint.__init__`.
- Stored it as `self.violation_error_code`.
- Passed `code=self.violation_error_code` to all `ValidationError` raises in `CheckConstraint.validate()` and `UniqueConstraint.validate()`.
- Included it in `BaseConstraint.deconstruct()`.
- Included it in `CheckConstraint.__eq__()` and `UniqueConstraint.__eq__()`.
- All 66 PASS_TO_PASS tests pass.

## 9. What v1 is missing

### CRITICAL: ExclusionConstraint not updated
`django/contrib/postgres/constraints.py` contains `ExclusionConstraint(BaseConstraint)` which was **completely missed** by v1. This class:
- Has its own `__init__` that accepts `violation_error_message` but NOT `violation_error_code` (line 26-36).
- Passes only `violation_error_message` to `super().__init__()` (line 63).
- Has `validate()` with two `raise ValidationError(self.get_violation_error_message())` calls (lines 207, 212) that don't pass `code=`.
- Has `__eq__` that compares `violation_error_message` but not `violation_error_code` (line 143-153).

### CRITICAL: __repr__ methods not updated
None of the three constraint classes (`CheckConstraint`, `UniqueConstraint`, `ExclusionConstraint`) include `violation_error_code` in their `__repr__` output. The existing `__repr__` methods conditionally include `violation_error_message` when it differs from the default. The same pattern should be followed for `violation_error_code` when it is not None.

## 10. Exact minimal changes for v2
In `django/db/models/constraints.py`:
1. `CheckConstraint.__repr__`: Add conditional `violation_error_code` display.
2. `UniqueConstraint.__repr__`: Add conditional `violation_error_code` display.

In `django/contrib/postgres/constraints.py`:
3. `ExclusionConstraint.__init__`: Add `violation_error_code=None` parameter and pass to `super().__init__()`.
4. `ExclusionConstraint.validate()`: Pass `code=self.violation_error_code` to both `ValidationError` raises.
5. `ExclusionConstraint.__eq__()`: Add `self.violation_error_code == other.violation_error_code` comparison.
6. `ExclusionConstraint.__repr__`: Add conditional `violation_error_code` display.

## 11. Forbidden changes (regression risk)
- Do not change the `unique_error_message()` call in `UniqueConstraint.validate()`.
- Do not add `violation_error_code` to the deprecated positional args path.
- Do not change `default_violation_error_message` or the `get_violation_error_message()` method signature.
- Do not modify any SQL generation methods.
