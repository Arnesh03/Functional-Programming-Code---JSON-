# Results

Every measured run, in the order it happened. Numbers are copied from
`results/metrics/*.json`, the `code_runs` tables and the dataset's `stats.json` — nothing here is
recalled from memory.

Two things to keep in mind while reading:

- **`overall` = mean of scope F1, relation F1, kind accuracy, parent accuracy.** It deliberately
  does **not** include depth, and it is frozen so early runs stay comparable.
- **`learning_score` = mean of all seven movable metrics** (the four above plus depth exact-rate,
  generator F1, entrypoint F1). Added later, for the self-improvement loop to optimise. Where a
  run predates it, it is not back-filled.

---

## 1. Dataset build

`python3 scripts/generate_nested_code.py --count 1000 --target-lines 700 --run-check 25 --clean`

| | |
|---|---|
| Programs | **1,000** |
| Total lines | **843,965** |
| Mean / min / max lines | 844 / 759 / 1,169 |
| AST nodes | 6,008,056 |
| Splits | train 800 · val 100 · test 100 |
| Files with recursion-inside-recursion | 390 |
| Files with mutual recursion | 390 |
| Rejected below floor or invalid | **0** |
| Duplicates discarded | **0** |
| Run-checked by the generator | 25 / 25 passed |
| Executed afterwards by hand | **1,000 / 1,000 passed** |

Measured block-depth distribution:

| depth | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---|---|---|---|---|---|---|
| files | 1 | 9 | 23 | 83 | 321 | 331 | 232 |

Zero rejections means the templates cleared the depth floor on the first attempt every time.

---

## 2. Plumbing checks — `gold` backend, no model

The gold backend replays the AST record through every stage after generation, so a 1.000 here
proves the chain (normalise → validate → score → persist → hierarchy) and nothing about model
skill.

| run | files | overall | schema-valid |
|---|---|---|---|
| `run_20261021_053401_gold` | 5 | **1.000** | 5/5 |
| `run_20261021_060003_gold` (on the GPU box) | 3 | **1.000** | 3/3 |
| `run_20261022_230956_gold` (after retrieval was added) | 3 | **1.000** | 3/3 |

Every sub-metric is 1.000 in all three: scope F1, kind, parent, relation F1, recursion F1,
generator F1, entrypoint F1, depth MAE 0.00 (exact 1.000).

---

## 3. Strategy comparison — one file, `nested_00002_D14_L9_B9` (830 lines, depth 14)

| run | model · strategy | scope F1 | kind | parent | rel F1 | recursion | depth MAE | overall | time |
|---|---|---|---|---|---|---|---|---|---|
| 1 | gold | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.00 | **1.0000** | 0.1 s |
| 2 | qwen3:4b · **single call** | 0.111 | 1.000 | 1.000 | 0.000 | — | 1.00 | **0.5278** | 114 s |
| 3 | qwen3:4b · **multicall** | 0.938 | 0.933 | 1.000 | 0.450 | 0.000 | 3.00 | **0.8302** | 1,172 s |
| — | gpt-oss:120b · multicall (H200) | 1.000 | 1.000 | 1.000 | 0.900 | 1.000 | 2.27 | **0.9750** | 110 s |
| — | gpt-oss:120b · multicall, after the sectioner fix | 1.000 | 1.000 | 1.000 | 0.952 | 1.000 | — | **0.9881** | 143 s |

The single-call collapse is the headline: **1 of 17 scopes returned**. A 4B model spends its whole
context reading 850 lines and has nothing left to answer with — the exact failure the OPORD build
wrote `multicall` for. Splitting on top-level `def`/`class` took it from 0.111 to 0.938 on the
same model and the same file.

A second local run, `nested_00111_D15_L6_B13` on qwen3:4b · multicall, scored **0.7222** in 281 s.

---

## 4. Main evaluation — 20 files, gpt-oss:120b · multicall, 4 × H200

`run_20261021_065227_multicall_h200.json` — 20 files, 46.2 min, **schema-valid 20/20**, 0 failures.

| metric | score |
|---|---|
| scope F1 (precision / recall) | **1.0000** (1.000 / 1.000) |
| kind accuracy | **1.0000** |
| parent accuracy | **1.0000** |
| recursion F1 | **1.0000** |
| relation F1 | 0.9106 |
| generator F1 | 0.6752 |
| depth MAE (exact rate) | 0.8437 (0.4894) |
| entrypoint F1 | **0.0000** ← a bug, fixed; see below |
| **overall** | **0.9776** |

### Per file

| file | depth | scope F1 | rel F1 | depth MAE | overall | time |
|---|---|---|---|---|---|---|
| nested_00073 | 15 | 1.000 | 0.938 | 0.69 | 0.984 | 156 s |
| nested_00134 | 16 | 1.000 | 0.933 | 1.10 | 0.983 | 98 s |
| nested_00151 | 16 | 1.000 | 0.895 | 0.33 | 0.974 | 209 s |
| nested_00191 | 15 | 1.000 | 0.929 | 1.74 | 0.982 | 157 s |
| nested_00192 | 15 | 1.000 | 0.765 | 0.85 | **0.941** ← worst | 132 s |
| nested_00231 | 15 | 1.000 | 0.973 | 0.77 | **0.993** ← best | 158 s |
| nested_00237 | 14 | 1.000 | 0.903 | 0.56 | 0.976 | 136 s |
| nested_00266 | 16 | 1.000 | 0.903 | 0.60 | 0.976 | 163 s |
| nested_00298 | 16 | 1.000 | 0.968 | 0.69 | 0.992 | 131 s |
| nested_00657 | 14 | 1.000 | 0.947 | 0.73 | 0.987 | 127 s |
| nested_00668 | 15 | 1.000 | 0.923 | 0.79 | 0.981 | 159 s |
| nested_00683 | 15 | 1.000 | 0.900 | 1.23 | 0.975 | 120 s |
| nested_00701 | 15 | 1.000 | 0.833 | 0.77 | 0.958 | 112 s |
| nested_00702 | 15 | 1.000 | 0.909 | 1.50 | 0.977 | 75 s |
| nested_00752 | 14 | 1.000 | 0.949 | 0.71 | 0.987 | 225 s |
| nested_00822 | 16 | 1.000 | 0.857 | 0.33 | 0.964 | 175 s |
| nested_00870 | 16 | 1.000 | 0.889 | 0.82 | 0.972 | 94 s |
| nested_00891 | 15 | 1.000 | 0.960 | 1.00 | 0.990 | 110 s |
| nested_00912 | 15 | 1.000 | 0.929 | 0.67 | 0.982 | 141 s |
| nested_00932 | 14 | 1.000 | 0.909 | 1.00 | 0.977 | 94 s |

**Scope F1 is 1.000 on every single file.** In 800-line programs nested 16 levels deep, the model
found every module, class, function and method, and got every parent link right.

---

## 5. Bugs the runs exposed

Each of these was found by a measurement, not by reading code.

| # | Symptom | Cause | Fix | Effect |
|---|---|---|---|---|
| 1 | `entrypoint F1 = 0.000` on all 20 files | the sectioner swallowed the `if __name__ == "__main__":` guard into the **last function's** section, so the module-level prompt never saw it | trailing module-level code becomes its own `module_trailer` section | **0.000 → 1.000**; file overall 0.975 → **0.9881** |
| 2 | `UnboundLocalError: level1` at runtime | the closure generator emitted `return level1` *before* `def level1` | emit inner defs before the return | all 1,000 files execute |
| 3 | `too many statically nested blocks` | CPython allows 20 nested blocks per code object; `try_pyramid` spent two per level | per-template depth caps | rejections 21 → **0** |
| 4 | "Expand all" silently re-folded the tree | an empty collapsed-set was read as "not initialised" | explicit `ready` flag | 43 → 250 nodes |
| 5 | Hierarchy tab blank on first open | only loaded on `change` | load on tab open | — |

---

## 5a. Why four scores are exactly 1.000 — read this before quoting them

Measured, not assumed. The four perfect scores have different causes, and two are partly
artifacts of this pipeline rather than model skill.

### scope F1 = 1.000 — the model is shown the name list

`build_section_prompt` puts the roster of top-level definitions into every section prompt:

> The file defines: sift_graph, probe_segment, fold_cohort, merge_bundle, Channel80, …

It is there so cross-section calls can resolve, but the effect is that the model is **confirming**
top-level names rather than discovering them. The sectioner also splits on a column-zero
`def`/`class` regex, so the top-level scope set is largely determined before the model is asked.

*What is still genuine:* 416 scopes across 20 files with no false positives, and **136 of them
(32.7%) are nested** — methods and inner functions the roster never names.

### parent accuracy = 1.000 — two-thirds of it is a default

| | count | share |
|---|---|---|
| scopes whose parent is the module | 280 | **67.3%** |
| genuinely nested scopes | 136 | 32.7% |

`merge_partials.py:76` assigns `parent_id = "module"` whenever the model reports no parent. So
for two-thirds of scopes the "correct" answer is filled in by the merger, not chosen by the model.
The real question is only asked on the other 136.

### recursion F1 = 1.000 — 7 of 20 files score it for free

`_prf(∅, ∅)` returns precision 1.0, recall 1.0, F1 1.0 — an empty prediction against an empty
truth is counted as perfect. Across the 20 files there are only **22 recursive scopes out of 416**,
and **7 files contain none at all**, so 35% of the per-file scores are free wins averaged in.

*What is still genuine:* on the 13 files that do contain recursion, it was identified correctly,
including recursion-inside-recursion and mutual recursion.

### kind accuracy = 1.000 — the task is syntactic

`module | class | function | async_function | method`. A `def` at column zero is a function, a
`def` inside a `class` is a method, `async def` is async. Reading it off the syntax is close to
mechanical; 1.000 is the expected result, not a surprising one.

### And the dataset is generated

All 1,000 files come from 13 templates, so they are far more regular than scraped code: stereotyped
`verb_noun` names, predictable shapes. Every number here would be harder to achieve on real code.

### The honest signal is the low scores

Depth exact 0.4894 and generator F1 0.6752 are **not** inflated by any of the above — they are
measured the same way and they are poor. That asymmetry is the evidence that the metrics are not
uniformly broken: the easy things score high, the hard thing scores low, which is what a working
measurement looks like.

### Three changes that would make these numbers honest

1. `_prf` should report *n/a* for an empty-vs-empty comparison instead of 1.0, and recursion F1
   should be averaged only over files that contain recursion.
2. Parent accuracy should be reported over **nested scopes only**, where the parent is a real choice.
3. An ablation with the roster removed from the section prompt would measure true scope discovery.

---

## 6. Where the remaining error is

Scope, kind, parent and recursion are saturated at 1.000. Everything left to win is in three
places:

| metric | score | what goes wrong |
|---|---|---|
| **depth exact rate** | **0.4894** | the model finds every scope but miscounts how deep its nesting goes — roughly half the scopes are off, MAE 0.84 |
| generator F1 | 0.6752 | `yield` buried inside a nested block gets missed |
| relation F1 | 0.9106 | occasional invented or missed call edges |

This is precisely what the self-improvement loop and retrieval were added to attack.

---

## 7. Training run — self-improvement with retrieval

```bash
RAG=1 LEARNED_HINTS=1 OLLAMA_MODEL=gpt-oss:120b \
  python3 scripts/auto_improve.py --rounds 2 --dev 6 --test 6 --strategy multicall
```

The first run of the complete architecture: retrieval over 3,305 solved train sections plus the
failure-mining loop. Nothing is trained in the machine-learning sense — there are no gradients and
no weights change. What improves is the **prompt working memory** in
`assets/eval/learned_hints.json`.

### 7.1 Baseline — before any hints

| split | `learning_score` |
|---|---|
| dev (6 files) | **0.7090** |
| test (6 files, held out) | **0.7896** |

**Why this is lower than the 0.9776 headline, and why that is correct.** `overall` averages four
metrics that sit at or near 1.000. `learning_score` averages all seven that a prompt change can
move, including `depth_exact_rate` (0.4894) and `generator_f1` (0.6752). Pulling the two weak
metrics into the objective is the entire point: optimising `overall` would be pointless, because a
prompt change that fixed depth perfectly would not move it by a single point.

The ~0.08 gap between dev and test is sampling noise across two 6-file draws, not a signal.

### 7.2 Round 1 — what the loop mined

From the 6 dev files, on its own, with no knowledge of the error analysis in
[metrics.md §12](metrics.md):

```
mined: 32 depth errors, mean delta -0.84
mined: 19 generator-flag errors
mined: relations: 0 invented, 42 missed
```

It wrote **4 rules and 3 corrected examples**. The depth rule it generated:

> *You are undercounting max_block_depth by 0.8 levels on average (32 scopes wrong this round).
> Count the longest chain of nested for / while / if / try / with / match by following the
> indentation down to the deepest statement, not by counting distinct constructs.*

### 7.3 The mining independently corroborates the error analysis

This is the part worth noticing. [metrics.md §12](metrics.md) analysed **350 scopes from the
20-file evaluation**. The loop mined a **different 6 files** and found the same structure:

| finding | §12 error analysis | round-1 mining | agree? |
|---|---|---|---|
| depth error direction | undercount, mean −0.329 | undercount, mean −0.84 | **yes** |
| generator errors | 23 missed, 0 invented | 19 errors, missed-dominated | **yes** |
| relation errors | 35 missed vs 11 invented (3:1) | **42 missed vs 0 invented** | **yes** |

Two independent samples, measured by two independently written pieces of code, reach the same
conclusion: **this model errs by omission, never by invention, and it undercounts deep nesting.**
That is strong evidence the error is a real property of the model on this task rather than an
artifact of one sample or one scoring path.

### 7.4 The acceptance gate

The candidate is re-measured on dev, then on the **held-out test split that was never used for
mining**. It is kept only if the held-out score strictly improves — a tie is a rejection, because
a gain on dev alone is memorisation of the three mined examples. A rejected candidate is rolled
back to the previous champion and the loop stops.

| round | dev | test (held out) | decision |
|---|---|---|---|
| 0 | 0.7090 | 0.7896 | baseline |
| 1 | **0.7737** (+0.065) | **0.7576** (−0.032) | **rejected, rolled back to v0** |

Finished in 84.1 minutes, 24 file-extractions. Working memory stayed at **v0** — nothing was kept.

### 7.5 The candidate was rejected, and that is the result

The mined hints **improved the files they were mined from and damaged everything else.**

| split | depth exact | overall |
|---|---|---|
| **dev** (the 6 files mined) | 0.598 → **0.665** (+0.067) | 0.883 → **0.938** (+0.055) |
| **test** (6 files never used for mining) | 0.702 → **0.652** (−0.050) | 0.957 → **0.912** (−0.044) |

Per-file, on the held-out split, **4 of 6 files got worse**:

| file | depth exact | |
|---|---|---|
| nested_00659 | 0.92 → 0.68 | **−0.24** |
| nested_00649 | 0.83 → 0.69 | −0.14 |
| nested_00279 | 0.55 → 0.46 | −0.09 |
| nested_00609 | 0.89 → 0.80 | −0.09 |
| nested_00679 | 0.73 → 0.75 | +0.02 |
| nested_00239 | 0.29 → **0.53** | **+0.24** |

And the spread widened: held-out `overall` went from a tight 0.932–0.983 to a scattered
0.809–0.991. The hints made the model *less consistent*, not more.

**This is textbook memorisation, caught.** A +6.5-point gain on dev is exactly what three
corrected examples drawn from those same dev files should produce. Had the loop measured only dev
— as a naive setup would — this run would have been reported as "retrieval and learned hints
work, +6.5 points". It would have been false, and the regression would have shipped.

The held-out gate is the only reason that did not happen. It is also why a **tie** is coded as a
rejection rather than an acceptance.

### 7.6 What it says about the hypothesis

The one genuinely encouraging signal: **nested_00239, the hardest file in the split (depth 16),
improved from 0.29 to 0.53** — the largest single move in the run. The rules may help precisely
where nesting is deepest, which is consistent with [metrics.md §12.2](metrics.md): the error is
concentrated at depth 8 and beyond. But one file is one file, and four others regressed.

The honest reading: **telling gpt-oss:120b to "count more carefully" does not generalise.** The
instruction is too blunt — it pushes the model to inflate depth everywhere, which helps the deep
cases and hurts the shallow ones it was already getting right. That matches the signed-error
data: baseline mean error is −0.33, so a global "you are undercounting" nudge over-corrects the
majority of scopes that were already correct.

**The next thing to try is structural, not instructional** — ask the model for the block list per
scope and *compute* `max_block_depth` from the parent links, the way `gold.py` does. Counting is
a job for the parser; the model should only be asked to report what it sees. That change was
pre-registered here before the result came in, and the result supports it.

### 7.7 What this validates

| | |
|---|---|
| The held-out gate | works — it caught a regression that dev-only measurement would have shipped |
| `learning_score` | works — depth moved the composite, which `overall` alone would have hidden |
| The mining | works — it found the right error structure (§7.3), the *remedy* was wrong |
| The rollback | works — hints stayed at v0, no state corrupted |

A negative result from a correctly-built experiment is worth more than a positive one from a
broken one. This run cost 84 minutes and told you something true: **this particular correction
does not generalise, and here is the evidence.**

An earlier attempt was started before retrieval existed and stopped at 11/12 baseline files; its
log is kept as `improve_pre_retrieval.log` on the GPU box. The no-retrieval baseline is
reproducible with `RAG=0`.


---

## 8. Second training run — CodeComplex (real code)

`DATASET_DIR=data/codecomplex ... auto_improve.py --rounds 2 --dev 20 --test 20 --strategy multicall`

The same loop, same model, against **real Codeforces submissions** instead of generated files.
Built by `scripts/build_codecomplex_dataset.py` from
[CodeComplex](https://github.com/sybaik1/CodeComplex): 4,701 files after removing 199 duplicate
submissions, 0 parse failures, splits 3761 / 470 / 470. Retrieval index rebuilt on its own train
split (1,714 sections from 1,500 files).

### 8.1 CodeComplex is real but shallow

Measured with `app.gold` over all 4,900 records:

| | CodeComplex | generated set |
|---|---|---|
| median lines | **24** | 844 |
| mean scopes per file | **2.9** | ~21 |
| files at block depth ≥ 8 | **22 of 4,900** (0.4%) | 1,000 of 1,000 |
| files at depth ≥ 10 | **4** | 1,000 |
| with recursion | 543 (11%) | 390 (39%) |

Contest submissions are written fast and short; they do not nest deeply. CodeComplex is therefore
**not** a substitute for the generated corpus. Its value is that the code is real — ad-hoc names,
tabs, no docstrings, structures a person chose.

### 8.2 Result — rejected again, for a different reason

| phase | depth exact | overall | `learning_score` |
|---|---|---|---|
| baseline · dev | 0.838 | 0.972 | **0.9565** |
| baseline · held-out | 0.792 | 0.967 | **0.9451** |
| candidate · dev | 0.838 | 0.981 | 0.9573 (**+0.0008**) |
| candidate · held-out | **0.815** | 0.946 | 0.9315 (**−0.0136**) |

Finished in 26.7 min, 80 extractions, rolled back to v0.

**The first run failed by memorisation; this one did not.** The dev gain was +0.0008 — effectively
zero — so the hints were not fitting the mined files. They simply did not help.

Depth on the held-out split moved 0.792 → 0.815, and `overall` fell 0.967 → 0.946. At the time I
read this as "the depth rule worked, the relation rule sank it".

> **That reading was wrong.** §9 tested it directly with a depth-only run and found the effect was
> inside the measurement noise. Both numbers above are within run-to-run drift. Read §9 before
> drawing anything from this paragraph.

### 8.3 What the two runs together establish

| | generated (deep) | CodeComplex (real, shallow) |
|---|---|---|
| baseline depth exact | ~0.49 | **0.79 – 0.84** |
| depth errors available to mine | 32 | **3** |
| dev movement | +0.065 (memorisation) | +0.0008 (flat) |
| held-out movement | −0.032 | −0.0136 |
| verdict | rejected | rejected |

**Depth difficulty tracks depth, not synthetic-ness.** On shallow real code the model is right
79–84% of the time; on deep generated code, 49%. The generated dataset is hard for the *right
reason* — because the nesting is deep — not because it is artificial. That is the single most
useful thing these two runs establish, and it is a validity argument for the dataset that could
not be made without a real-code comparison.

A second point: with only **3 depth errors** available to mine from 20 real files, there is almost
no training signal in shallow code. A self-improvement loop needs failures to learn from, and
CodeComplex does not supply enough of them.

### 8.4 Next experiment this suggests

Split the mined rules and test them separately: a depth-only candidate should be accepted on
CodeComplex if the reading in 8.2 is right. That is a one-line change to `mine()` and a 27-minute
run — the cheapest decisive test available.


---

## 9. Third run — depth rules only, and the measurement-noise finding

`--rules depth --seed 21` on CodeComplex: identical splits to §8, the only change being that
`mine()` wrote **depth rules alone**, no flag or relation rules. A `--rules` flag was added to
`auto_improve.py` for this.

### 9.1 Result — rejected, and the effect vanished

| phase | depth exact | overall | `learning_score` |
|---|---|---|---|
| baseline · dev | 0.887 | 0.979 | **0.9672** |
| baseline · held-out | 0.805 | 0.949 | **0.9372** |
| candidate · dev | 0.766 | 0.987 | 0.9545 (**−0.0127**) |
| candidate · held-out | 0.818 | 0.958 | 0.9367 (**−0.0005**) |

24.6 min, 80 extractions, rolled back to v0. The depth rule alone made **dev worse** and left the
held-out split unchanged to within half a thousandth.

### 9.2 The real finding: the experiment cannot resolve effects this small

Both CodeComplex runs used **the same seed and therefore the same 20 dev and 20 held-out files**.
The baselines should have been identical. They were not:

| baseline metric | run §8 | run §9 | drift |
|---|---|---|---|
| `learning_score` dev | 0.9565 | 0.9672 | **+0.0107** |
| `learning_score` held-out | 0.9451 | 0.9372 | −0.0079 |
| `overall` held-out | 0.9670 | 0.9490 | **−0.0180** |
| **`depth_exact` dev** | 0.8380 | 0.8870 | **+0.0490** |
| `depth_exact` held-out | 0.7920 | 0.8050 | +0.0130 |

Same inputs, same code, same model — different numbers, purely from sampling at
`LLM_TEMPERATURE=0.2`. **The measurement floor is roughly ±0.011 on `learning_score` and as much
as ±0.05 on `depth_exact`.**

Now compare that to the effects being chased:

| effect | size | verdict |
|---|---|---|
| §8 held-out change (all rules) | −0.0136 | at the noise floor |
| §9 held-out change (depth only) | −0.0005 | **far below it** |
| the depth gain inferred in §8.2 | +0.0230 | **inside `depth_exact` drift of ±0.049** |
| §7 dev gain on the generated set | **+0.0650** | ~6× the floor — **real** |
| §7 held-out drop on the generated set | −0.0320 | ~3× the floor — **real** |

### 9.3 What survives, and what does not

**Survives.** The §7 memorisation result on the generated set: a +0.065 dev gain against a −0.032
held-out drop is three to six times the noise floor, and the rejection there was correct and
meaningful.

**Does not survive.** Every conclusion drawn from the two CodeComplex runs about *which rule
family helps*. Those effects are smaller than the drift between two identical baselines. The
honest statement is: **on shallow real code, mined prompt hints produce no measurable effect in
either direction**, and §8.2's attribution to the relation rule was reading signal into noise.

### 9.4 What the design needs before it can answer this question

1. **`LLM_TEMPERATURE=0` (greedy).** Most of this drift is sampling. Greedy decoding would make
   repeat runs reproducible and should collapse the floor substantially.
2. **More files per split.** Standard error scales with 1/√n; 20 files is too few for effects of
   1–2 points.
3. **A repeated baseline.** Measure the baseline two or three times and report its spread, so the
   acceptance threshold can be set above the noise rather than at zero.

As it stands the loop's gate is "strictly better on held-out", which with a ±0.011 floor will
accept noise roughly half the time it sees a true zero effect. It has rejected three times running,
so no false acceptance has occurred — but that is luck, not design.

### 9.5 Status after three runs

| run | corpus | rules | held-out change | verdict |
|---|---|---|---|---|
| §7 | generated (deep) | all | −0.0320 | rejected — real memorisation |
| §8 | CodeComplex (real) | all | −0.0136 | rejected — within noise |
| §9 | CodeComplex (real) | depth only | −0.0005 | rejected — within noise |

Working memory remains at **v0**. Nothing has been learned that generalises, and the fastest way
to change that is the structural fix in §7.6 — ask the model for the block list per scope and
compute `max_block_depth` from the parent links — rather than more prompt wording.
