# FINDINGS — SkyCoord.__getattr__ Descriptor Error Propagation

## Finding 1 — Root cause: __getattr__ masks descriptor errors (the reported bug)

**Evidence**: When a SkyCoord subclass defines a property whose getter raises `AttributeError` internally (e.g., accessing a non-existent attribute), `__getattr__` is invoked with the property's name. The method cannot distinguish "attr truly doesn't exist" from "attr exists as a descriptor but its __get__ failed." It always raises the generic error.

**Input → observed vs expected**:
```python
class custom_coord(SkyCoord):
    @property
    def prop(self):
        return self.random_attr

c = custom_coord('00h42m30s', '+41d12m00s', frame='icrs')
c.prop
```
- **Observed**: `AttributeError: 'custom_coord' object has no attribute 'prop'`
- **Expected**: `AttributeError: 'custom_coord' object has no attribute 'random_attr'`

**Classification**: Code bug — misleading error message masks the real missing attribute.

## Finding 2 — v1 fix is correctly placed after all frame lookups

**Evidence**: The descriptor re-invocation check is placed between the last frame lookup (`transform_to`) and the final `raise AttributeError`. This means frame attributes, frame names, and frame transformations all take precedence over the descriptor check. This is correct because:
- If `attr` matches a frame name or attribute, the frame lookup succeeds before reaching the descriptor check
- The descriptor check only fires when all SkyCoord-specific lookups have failed

**Classification**: Positive finding — correct ordering preserves all existing SkyCoord behavior.

## Finding 3 — `hasattr(desc, '__get__')` is appropriately general

**Evidence**: Using `hasattr(desc, '__get__')` rather than `isinstance(desc, property)` handles:
- `property` descriptors (the reported case)
- `functools.cached_property`
- Custom descriptors with `__get__`
- Slot descriptors (`__slots__`)

Regular functions also have `__get__` but their `__get__` returns a bound method (never raises `AttributeError`), so `__getattr__` would never be called for them. The check is safe.

**Classification**: Positive finding — appropriately general without over-catching.

## Finding 4 — Descriptor re-invocation invokes the getter twice

**Evidence**: The property getter is called once by Python's normal lookup (which fails), then once more by our fix. This means:
- Side effects in property getters execute twice
- Properties should be side-effect-free per convention
- This is the standard approach used in Python (cf. StackOverflow link in the issue)

**Classification**: Known trade-off — acceptable because property getters should be idempotent.

## Finding 5 — No recursion risk

**Evidence**: Tracing the call chain:
1. `__getattr__('prop')` re-invokes `prop.__get__`
2. Inside getter, `self.random_attr` triggers `__getattr__('random_attr')`
3. `random_attr` is not a descriptor → raises generic error
4. Error propagates through `prop.__get__` → out of `__getattr__('prop')`

The recursion terminates because the leaf attribute (`random_attr`) is not a descriptor.

For nested properties (property A calls property B which fails), the same logic applies: each `__getattr__` call invokes the descriptor at most once, and the chain terminates at the non-descriptor leaf.

**Classification**: Positive finding — no infinite recursion.

## Finding 6 — Initialization safety preserved

**Evidence**: During `__init__`, `_sky_coord_frame` is not yet in `self.__dict__`, so the `if` block is skipped. The descriptor check runs outside the `if` block. If a descriptor is accessed during init and its `__get__` fails, the fix re-invokes it (which fails again), propagating the original error. This is equivalent to the existing behavior (raise `AttributeError`) but with a better message. No new failure modes.

**Classification**: Positive finding — safe during initialization.

## Proof-derived findings from analysis

No additional issues found. The v1 fix is minimal, correctly placed, and handles all identified edge cases.
