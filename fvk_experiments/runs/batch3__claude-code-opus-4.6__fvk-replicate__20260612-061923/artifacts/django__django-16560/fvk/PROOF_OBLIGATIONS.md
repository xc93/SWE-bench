# Proof Obligations

## Bug-revealing obligations (FAIL_TO_PASS)

### O1: BaseConstraint accepts violation_error_code
- BaseConstraint(name="n", violation_error_code="c") must set self.violation_error_code = "c"
- BaseConstraint(name="n") must set self.violation_error_code = None

### O2: BaseConstraint.deconstruct includes violation_error_code
- When violation_error_code is not None, kwargs must include it
- When violation_error_code is None, kwargs must NOT include it

### O3: BaseConstraint.clone preserves violation_error_code
- clone() must round-trip violation_error_code through deconstruct/reconstruct

### O4: CheckConstraint with violation_error_code
- CheckConstraint(check=Q(...), name="n", violation_error_code="c") stores code
- CheckConstraint.validate raises ValidationError with code="c"
- CheckConstraint.__eq__ considers violation_error_code

### O5: UniqueConstraint with violation_error_code
- UniqueConstraint(fields=(...), name="n", violation_error_code="c") stores code
- UniqueConstraint.validate raises ValidationError with code="c"
- UniqueConstraint.__eq__ considers violation_error_code

### O6: ExclusionConstraint with violation_error_code
- ExclusionConstraint(name="n", expressions=[...], violation_error_code="c") stores code
- ExclusionConstraint.validate raises ValidationError with code="c"
- ExclusionConstraint.__eq__ considers violation_error_code

## Non-regression obligations (PASS_TO_PASS)

### O7: Default behavior unchanged
- When violation_error_code is not provided, ALL existing behavior is preserved
- ValidationError raised with code=None (same as original)
- deconstruct output unchanged for existing constraints
- __eq__ unchanged for constraints without violation_error_code
- __repr__ unchanged for constraints without violation_error_code

### O8: Existing violation_error_message behavior unchanged
- violation_error_message still works as before
- get_violation_error_message() still returns formatted string
- default_violation_error_message still works

### O9: validate_constraints interaction
- validate_constraints in base.py still correctly groups errors
- code="unique" from unique_error_message still works when no custom code set

### O10: ExclusionConstraint backward compat
- ExclusionConstraint without violation_error_code must work as before
- ExclusionConstraint deconstruct must not include violation_error_code when None
