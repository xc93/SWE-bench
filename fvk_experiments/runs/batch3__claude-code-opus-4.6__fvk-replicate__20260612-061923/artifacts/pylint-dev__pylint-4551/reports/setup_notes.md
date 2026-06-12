# Setup Notes

## Environment
- Python 3.9.25 via uv venv
- Pylint 2.9.0-dev1 installed editable from repo/
- Astroid 2.6.6
- pytest 8.4.2

## Verification
- Repo checked out at truncated single commit (hash d18a41c, content matches base commit 99589b0)
- `import pylint` works, version 2.9.0-dev1
- Existing pyreverse tests pass: 14/14 (unittest_pyreverse_inspector + unittest_pyreverse_writer)
- SETUPTOOLS_SCM_PRETEND_VERSION=2.9 used during install (truncated history has no tags)
