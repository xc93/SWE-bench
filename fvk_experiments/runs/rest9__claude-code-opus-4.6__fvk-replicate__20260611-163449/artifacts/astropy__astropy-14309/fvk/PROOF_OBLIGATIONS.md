# PROOF OBLIGATIONS — astropy__astropy-14309

## Bug-fix obligation

**PO-1**: `is_fits(origin, filepath, fileobj)` (no extra args) must return `False` without raising, when `filepath` is a non-FITS path and `fileobj` is None.

**Status**: Satisfied by v1. `bool(args)` short-circuits to `False`.

## Non-regression obligations

**PO-2**: `is_fits(origin, filepath, fileobj, hdulist)` where `hdulist` is an `HDUList` must still return `True`.

**Status**: Satisfied by v1. `bool(args)` is True, then `isinstance(args[0], ...)` evaluates as before.

**PO-3**: `is_fits(origin, "file.fits", None)` must still return `True`.

**Status**: Satisfied by v1. The `filepath.lower().endswith(...)` branch fires first, returning `True` before reaching the modified line.

**PO-4**: `is_fits(origin, None, fileobj)` where `fileobj` contains a FITS signature must still return `True`.

**Status**: Satisfied by v1. The `fileobj is not None` branch fires first.

**PO-5**: `is_fits(origin, "file.ecsv", None, non_fits_obj)` must still return `False`.

**Status**: Satisfied by v1. `bool(args)` is True, `isinstance(args[0], ...)` is False.

**PO-6**: All 141 existing tests in `test_connect.py` must pass.

**Status**: Verified — 141 passed, 8 skipped, 5 xfailed.

**PO-7**: All 221 existing tests in `test_registries.py` must pass.

**Status**: Verified — 221 passed, 14 skipped.

## Scope constraint obligations

**PO-8**: The patch must only modify `astropy/io/fits/connect.py`.

**Status**: Satisfied by v1. Single file, single line change.

**PO-9**: The patch must not modify `astropy/io/votable/connect.py` or any other identifier function.

**Status**: Satisfied by v1. Finding 2 (votable) is noted but not fixed.

**PO-10**: The patch must not change the function signature, imports, or any other behavior of `is_fits`.

**Status**: Satisfied by v1. Only the return expression on line 72 is modified.
