# Iteration Guidance: v1 -> v2

## What v1 got right
1. Added violation_error_code to BaseConstraint class attribute, __init__, deconstruct, clone
2. Added get_violation_error_code() method
3. Updated CheckConstraint: __init__, validate, __eq__
4. Updated UniqueConstraint: __init__, validate (all 3 branches), __eq__
5. Preserved backward compatibility: default None code, no change to existing behavior

## What v1 missed (root cause of 2/8 test failures)

### CRITICAL: ExclusionConstraint not updated
`django/contrib/postgres/constraints.py` defines `ExclusionConstraint(BaseConstraint)` which also needs:
1. `violation_error_code=None` parameter in `__init__`
2. Forward `violation_error_code` to `super().__init__()`
3. Pass `code=self.violation_error_code` to `ValidationError` in `validate()`
4. Include `violation_error_code` in `__eq__`

This is the most likely cause of the 2 remaining test failures.

## Exact v2 changes

### File: django/contrib/postgres/constraints.py

1. **__init__ (line 26-36)**: Add `violation_error_code=None` parameter
2. **super().__init__ (line 63)**: Add `violation_error_code=violation_error_code`
3. **validate (lines 207, 212)**: Change both `ValidationError(self.get_violation_error_message())` to `ValidationError(self.get_violation_error_message(), code=self.violation_error_code)`
4. **__eq__ (lines 143-153)**: Add `and self.violation_error_code == other.violation_error_code`

### File: django/db/models/constraints.py
No additional changes needed (v1 changes are correct).

## Forbidden changes
- Do NOT change default behavior when violation_error_code is None
- Do NOT change violation_error_message behavior
- Do NOT change __repr__ (no tests expected for this)
- Do NOT change validate_constraints in base.py
- Do NOT modify the deprecated positional arguments path
