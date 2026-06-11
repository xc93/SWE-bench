# SWE-bench Verified FVK experiment: `sympy__sympy-17630`

You are a fresh coding agent. Run a controlled Formal Verification Kit experiment on `sympy__sympy-17630`.

Goal: determine whether applying FVK after an ordinary first patch improves, worsens, or does not change the aggregate SWE-bench result.

## Instance

- Dataset: `princeton-nlp/SWE-bench_Verified`, split `test`, HF row offset `461`
- Instance ID: `sympy__sympy-17630`
- Repository: `sympy/sympy` / `https://github.com/sympy/sympy.git`
- Base commit: `58e78209c8577b9890e957b624466e5beed7eb08`
- Version: `1.5`
- Difficulty: `1-4 hours`
- Language: Python
- FVK: `https://github.com/grosu/formal-verification-kit`

Evaluator shape, counts only:

- `FAIL_TO_PASS`: 2 tests
- `PASS_TO_PASS`: 19 tests
- Resolved iff `2/2` FAIL_TO_PASS and `19/19` PASS_TO_PASS.

## Mandatory benchmark discipline

- Generate patches using only this prompt, `benchmark/public_instance.json`, `benchmark/PROMPT.md`, the base repo/source, existing public tests, and FVK artifacts you create.
- Do NOT inspect/use the gold `patch`.
- Do NOT manually inspect/use hidden `test_patch`.
- Do NOT inspect hidden test names, hidden assertions, hidden failure traces, private evaluator logs, private JUnit XML, or hidden patch contents.
- Do NOT open `private_eval/swebench_row_full.json`; it exists only for `scripts/private_eval.py` to mechanically produce aggregate-only scores.
- Do NOT search the web/Hugging Face/GitHub PRs/issues for the original solution or for `sympy__sympy-17630`.
- Before v2 you may use only the aggregate v1 score: `FAIL_TO_PASS A/2`, `PASS_TO_PASS B/19`, `resolved true/false`.
- FVK must accumulate findings/guidance; it must not silently patch code by itself.

## Public problem statement

```text
Exception when multiplying BlockMatrix containing ZeroMatrix blocks
When a block matrix with zero blocks is defined

```
>>> from sympy import *
>>> a = MatrixSymbol("a", 2, 2)
>>> z = ZeroMatrix(2, 2)
>>> b = BlockMatrix([[a, z], [z, z]])
```

then block-multiplying it once seems to work fine:

```
>>> block_collapse(b * b)
Matrix([
[a**2, 0],
[0, 0]])
>>> b._blockmul(b)
Matrix([
[a**2, 0],
[0, 0]])
```

but block-multiplying twice throws an exception:

```
>>> block_collapse(b * b * b)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/matrices/expressions/blockmatrix.py", line 297, in block_collapse
    result = rule(expr)
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/strategies/core.py", line 11, in exhaustive_rl
    new, old = rule(expr), expr
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/strategies/core.py", line 44, in chain_rl
    expr = rule(expr)
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/strategies/core.py", line 11, in exhaustive_rl
    new, old = rule(expr), expr
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/strategies/core.py", line 33, in conditioned_rl
    return rule(expr)
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/strategies/core.py", line 95, in switch_rl
    return rl(expr)
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/matrices/expressions/blockmatrix.py", line 361, in bc_matmul
    matrices[i] = A._blockmul(B)
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/matrices/expressions/blockmatrix.py", line 91, in _blockmul
    self.colblocksizes == other.rowblocksizes):
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/matrices/expressions/blockmatrix.py", line 80, in colblocksizes
    return [self.blocks[0, i].cols for i in range(self.blockshape[1])]
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/matrices/expressions/blockmatrix.py", line 80, in <listcomp>
    return [self.blocks[0, i].cols for i in range(self.blockshape[1])]
AttributeError: 'Zero' object has no attribute 'cols'
>>> b._blockmul(b)._blockmul(b)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/matrices/expressions/blockmatrix.py", line 91, in _blockmul
    self.colblocksizes == other.rowblocksizes):
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/matrices/expressions/blockmatrix.py", line 80, in colblocksizes
    return [self.blocks[0, i].cols for i in range(self.blockshape[1])]
  File "/home/jan/.pyenv/versions/3.7.4/lib/python3.7/site-packages/sympy/matrices/expressions/blockmatrix.py", line 80, in <listcomp>
    return [self.blocks[0, i].cols for i in range(self.blockshape[1])]
AttributeError: 'Zero' object has no attribute 'cols'
```

This seems to be caused by the fact that the zeros in `b._blockmul(b)` are not `ZeroMatrix` but `Zero`:

```
>>> type(b._blockmul(b).blocks[0, 1])
<class 'sympy.core.numbers.Zero'>
```

However, I don't understand SymPy internals well enough to find out why this happens. I use Python 3.7.4 and sympy 1.4 (installed with pip).

```

## Public hints / discussion text

```text

```

## Workspace layout already staged

```text
benchmark/public_instance.json          # public fields only
benchmark/PROMPT.md                     # public prompt only
private_eval/swebench_row_full.json     # DO NOT OPEN; evaluator input only
scripts/private_eval.py                 # aggregate-only evaluator helper
EXPERIMENT_PROMPT.md
LAUNCH_INSTRUCTIONS.md
RUN_PROMPT.md
```

Use/create: `repo/`, `patches/`, `reports/`, `fvk/`.

## Phase 0: clone/setup

Clone `https://github.com/sympy/sympy.git` into `repo/`, check out `58e78209c8577b9890e957b624466e5beed7eb08`, and create a Python environment. Prefer repo instructions; practical fallback:

```bash
uv venv --python 3.9 .venv || uv venv --python 3.11 .venv || python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip setuptools wheel
python -m pip install -e . || true
python -m pip install pytest || true
```

Install enough public test dependencies to run relevant tests. Record commands in `reports/setup_notes.md`.

## Phase 1: v1 without FVK

Create an ordinary first patch in `repo/` using public information only. You may run existing public tests. Save:

```bash
cd repo && git diff > ../patches/solution_v1.patch && cd ..
```

Write `reports/v1_notes.md`.

## Phase 2: aggregate-only v1 evaluation

Try:

```bash
source .venv/bin/activate
python scripts/private_eval.py patches/solution_v1.patch v1 | tee reports/v1_score.md
```

If the generic evaluator is unsuitable, write a repo-specific aggregate-only evaluator under `scripts/`, preserving the same no-peeking/no-printing discipline. Do not read private logs. Record limitations in `reports/evaluator_notes.md`.

## Phase 3: FVK

Clone/read FVK:

```bash
git clone https://github.com/grosu/formal-verification-kit.git fvk_repo
```

Read `README.md`, `AGENTS.md`, `commands/formalize.md`, and `commands/verify.md`. Use slash commands if available; otherwise manually follow them.

Allowed FVK inputs: public prompt/source/tests, `patches/solution_v1.patch`, `reports/v1_notes.md`, `reports/v1_score.md` aggregate only.

Forbidden FVK inputs: gold patch, test_patch content, hidden test names/assertions/traces, private logs/JUnit.

Write `fvk/SPEC.md`, `fvk/FINDINGS.md`, `fvk/PROOF_OBLIGATIONS.md`, `fvk/PROOF.md` if useful, and `fvk/ITERATION_GUIDANCE.md`. Include both intended behavior and non-regression obligations.

## Phase 4: v2 using FVK guidance

Modify `repo/` conservatively. Every v2 change must trace to an FVK finding/obligation. Save:

```bash
cd repo && git diff > ../patches/solution_v2.patch && cd ..
```

Write `reports/v2_notes.md`.

## Phase 5: aggregate-only v2 evaluation

Run the same aggregate-only evaluator and save `reports/v2_score.md`.

## Final report

Write `reports/final_report.md` with:

- benchmark metadata;
- evaluator shape;
- discipline checklist;
- public problem summary;
- v1 patch/files/tests and v1 score;
- FVK artifacts and key findings;
- v2 patch/files/tests and v2 score;
- delta;
- direct answer: did FVK help, hurt, or only confirm/guard against regressions;
- artifact paths.

Final Claude response should be compact YAML with instance, v1 score, v2 score, delta, discipline status, and artifact paths. Do not include hidden test names/assertions/traces/patches.
