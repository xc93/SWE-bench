# Setup Notes

## Verification

- Repo HEAD: `e8420d750ec5f9e0efa3c3aadf5f88be8f44fd5f` (commit message: "base")
- The workspace uses a rebased/squashed base commit rather than the exact upstream hash `cdb66059a2feb44ee49021874605ba90801f9986`, but astropy 5.1 is installed and functional.
- `.venv/bin/python` imports astropy 5.1 correctly.
- pytest 7.4.0 is available.
- Registry tests pass: 221 passed, 14 skipped.
- FITS connect tests pass: 141 passed, 8 skipped, 5 xfailed.
- The reported bug reproduces exactly as described in the issue.

## No repairs needed

The pre-built environment worked as staged.
