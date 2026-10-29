# Nested Python code dataset

1,000 long, deeply nested Python programs — 843,965 lines, mean 844 lines per file, every one
parsed, compiled and executed before it entered the dataset. Nothing shallow is in here: the
floor is enforced by measurement, not by intent.

Built by [`scripts/generate_nested_code.py`](../../scripts/generate_nested_code.py).

## Layout

```
generated/
  nested_00001_D16_L11_B10.py   one program per file; D/L/B = measured block/loop/branch depth
  manifest.jsonl                one record per program: id, path, split, metrics  (655 KB)
  dataset.jsonl                 the same records plus the full source text        (36 MB)
  stats.json                    dataset-level distributions
  asts/<id>.json                flat py150-shape AST per program (only with --with-ast)
```

`dataset.jsonl` is the one to load for training — it needs no directory walk:

```python
import json
rows = [json.loads(l) for l in open("data/nested_code/generated/dataset.jsonl")]
train = [r for r in rows if r["split"] == "train"]   # 800 / 100 / 100 train / val / test
print(train[0]["metrics"]["block_depth"], len(train[0]["source"]))
```

## What is in each program

Every file is assembled from randomly chosen, randomly parameterised unit templates, each of
which nests the way working code nests. Counts are the number of files containing at least one
unit of that kind:

| unit | files | what it nests |
|---|---|---|
| `loop_pyramid` | 1000 | `for`/`while` chains with a branch ladder at the floor |
| `branch_pyramid` | 1000 | `if`/`elif`/`else` ladders inside one another |
| `match_nested` | 409 | `match`/`case` inside `match`/`case` inside loops |
| `closure_tower` | 401 | `def` inside `def` inside `def`, closing over every level |
| `try_pyramid` | 400 | `try`/`except`/`else`/`finally` nested through loops |
| `comprehension` | 398 | comprehensions inside comprehensions, with conditions |
| `state_machine` | 397 | `while` + `try` + `for`/`else` + `break`/`continue` |
| `recursion` | 390 | self-recursion, recursion inside recursion, mutual recursion |
| `with_pyramid` | 383 | context managers nested through loops |
| `class_tower` | 379 | a class with an inner class and deeply nested methods |
| `generators` | 378 | `yield` / `yield from` chains across nested loops |
| `data_walk` | 377 | recursive descent over a deeply nested literal |
| `async_nested` | 227 | `async with` / `async for` / `await` nested in loops |

Every unit is called from a `pipeline_<id>()` function at the bottom of the file, so no part of
any program is dead code. Running a file executes all of it.

## Measured depth

Depths are not asserted by the templates — each file is re-parsed with the stdlib `ast` module
and measured, and a sample that comes out shallower than the floor is thrown away and
regenerated. `block_depth` is the deepest chain of block-introducing statements
(`for`/`while`/`if`/`try`/`with`/`def`/`class`/`match`) — the closest thing to indentation depth.

```
block_depth   10:1  11:9  12:23  13:83  14:321  15:331  16:232
loop_depth     5:46  6:83  7:113   8:146  9:157  10:223  11:232
branch_depth   7:40  8:75  9:104  10:141 11:150  12:244  13:246
try_depth      1:600 4:38  5:47    6:315
with_depth     0:481 2:136 ... 10:62
data_depth    12:1000      (nesting of dict/list/tuple literals)
```

390 files contain recursion inside recursion; the same 390 contain mutual recursion.
Each `metrics` record also carries `n_lines`, `n_chars`, `n_ast_nodes`, `n_functions`,
`n_async_functions`, `n_classes`, `comprehension_depth`, `function_depth`,
`recursive_functions`, `nested_recursion` and `mutual_recursion`.

## Guarantees

* **Valid** — every file is `ast.parse`d and `compile`d before it is written.
* **Runnable** — all 1,000 were executed to completion under `python3 -I`; the generator
  re-checks a random sample (`--run-check N`) on every build and exits non-zero on a failure.
* **Nested** — enforced floors of `block_depth >= 8`, `loop_depth >= 4`, `branch_depth >= 4`,
  `n_lines >= 700`. 0 samples were rejected on the build that produced this dataset, meaning
  the templates cleared the floor on the first attempt every time.
* **Unique** — SHA-256 deduplicated; 0 duplicates.

## Regenerating

```bash
python3 scripts/generate_nested_code.py --count 1000 --target-lines 700 --run-check 25 --clean
```

Useful knobs: `--seed`, `--min-depth` / `--max-depth` (per-unit nesting), `--min-block-depth`
/ `--min-loop-depth` / `--min-branch-depth` (the rejection floor), `--with-ast` (also writes
`asts/<id>.json`, ~350 KB per file), `--out`.

The build is deterministic for a given `--seed`, so the dataset is reproducible from the script
alone.

## A note on py150

`build_nested_code_dataset.py` filters the scraped py150 corpus down to its nested files; that is
a different thing from this directory, which generates nesting to order. The scraped route gives
real-world code but a long tail of shallow files; this one gives a controlled depth spread with
no shallow samples at all.
