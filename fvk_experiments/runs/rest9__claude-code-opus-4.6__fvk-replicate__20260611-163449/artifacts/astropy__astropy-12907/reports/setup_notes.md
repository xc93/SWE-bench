# Setup Notes

## Verified

- repo/ HEAD: d607e9806a5ab5961c27c89e137f892aede024ed (shallow "base" commit)
- astropy version: 4.3
- pytest version: 7.4.0
- Existing separable tests pass: 11/11
- Bug reproduced: nested `Pix2Sky_TAN() & cm` gives incorrect coupled matrix

## Notes

- The repo HEAD hash differs from the stated base commit d16bfe05a744909de4b27f5875fe0d4ed41ce607 because this is a shallow/staged workspace clone. The code content matches astropy 4.3 at the expected state.
- No environment repairs needed.
