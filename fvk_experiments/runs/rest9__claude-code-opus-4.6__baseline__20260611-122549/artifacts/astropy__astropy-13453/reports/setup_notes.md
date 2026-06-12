# Setup Verification

- repo HEAD: `3435935af1105d84c60c2f7a9c04c73589e01044` (commit message: "base") — the environment_setup_commit, not the base_commit directly, but the repo source matches the expected state.
- `.venv/bin/python` imports astropy 5.0 correctly.
- pytest runs and passes: `astropy/io/ascii/tests/test_html.py` — 9 passed, 16 skipped (bs4 not installed).
