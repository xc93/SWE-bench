# v2 Notes

## How v2 differs from v1

v2 adds a guard condition to only compute `world_ref` when there are actually dropped world dimensions (`len(self._world_keep) < self._wcs.world_n_dim`). This avoids an unnecessary `_pixel_to_world_values_all` call when all world dimensions are kept (the common case in most existing tests).

The core fix is identical: dropped world dimensions use `world_ref[iworld]` instead of `1.`.

## Which review findings caused the change

Finding #9 (minor inefficiency): `world_ref` was computed unconditionally on every `world_to_pixel_values` call, even when there are no dropped world dimensions to fill.

## Regression risks v2 is designed to avoid

- The guard condition only skips computation that was already unused (the `else` branch is never entered when all world dims are kept).
- The `world_ref` variable is only referenced inside the `else` branch, which is only entered when there ARE dropped dims, which is exactly when the guard condition permits computation.
- No other code paths are modified.
