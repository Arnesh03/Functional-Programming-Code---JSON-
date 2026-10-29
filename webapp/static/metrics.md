# What every score means, and how to read it

Reference for the numbers in [results.md](results.md). Every formula below is the one actually in
[`app/evaluate.py`](../app/evaluate.py) — read off the code, not described from memory.

---

## 0. Two things that apply to all of them

### Matching is by bare name, never by `scope_id`

Two records can describe the same file correctly and still disagree about whether a path is
`module.Counter.tally` or `Counter.tally`. Penalising that would measure prompt compliance, not
whether the model read the code. So `_scope_index()` keys every scope by its **bare name**, and
parent links are compared by the **parent's name** too.

*Consequence:* if a file declared two different functions with the same name in different
namespaces, only the first is scored. The generator gives every definition a unique name, so this
does not bite here — but it would on real code.

### Files are weighted equally

`aggregate()` takes the mean of per-file scores. A 1,169-line file with 47 scopes counts exactly
as much as a 759-line file with 18. That is deliberate — otherwise a handful of large files would
decide the headline — but it means the aggregate is "the average file's score", not "the score
over all scopes".

---

## 1. Scope F1 — *did it find the right set of definitions?*

```python
pred = {bare name of every scope the model reported}
gold = {bare name of every scope the parser found}
tp = len(pred & gold)
precision = tp / len(pred)      # of what it reported, how much was real
recall    = tp / len(gold)      # of what exists, how much it found
f1        = harmonic mean
```

**Reading it.** Precision below 1 means invented scopes — names that do not exist in the file.
Recall below 1 means missed scopes. F1 balances the two.

**Your result: 1.000 / 1.000 / 1.000 across 20 files, 416 scopes, zero invented, zero missed.**
Caveat in [results.md §5a](results.md): the roster of top-level names is in the prompt, so the
real work was the 136 nested scopes (32.7%), not the 280 top-level ones.

**What a bad score looks like:** qwen3:4b single-call scored **0.111** — it returned 1 of 17.
Precision was 1.000 (the one name it gave was real) and recall 0.0588. That pair is the signature
of a model that ran out of context, not one that hallucinated.

---

## 2. Kind accuracy — *did it classify each definition correctly?*

```python
shared = names in both pred and gold
kind_accuracy = (# of shared names where pred.kind == gold.kind) / len(shared)
```

Computed **only over scopes both records agree exist**, so it is independent of scope F1: a model
that finds half the scopes but types them all correctly still scores 1.000 here.

**Values:** `module` · `class` · `function` · `async_function` · `method` · `async_method`.

**Your result: 1.000.** Expected — the distinction is syntactic (`def` at column zero is a
function, `def` inside a `class` is a method, `async def` is async).

---

## 3. Parent accuracy — *did it place each definition in the right namespace?*

Same shape as kind accuracy, comparing `_parent_name` — the **name** of the enclosing scope.

**Your result: 1.000**, but 67.3% of scopes are module-level and
[`merge_partials.py:76`](../app/multicall/merge_partials.py:76) assigns `parent_id = "module"`
whenever the model reports no parent. So two-thirds of the judgments are a default the pipeline
supplies. The number that would mean something is parent accuracy over the 136 nested scopes
alone, which this metric does not currently isolate.

---

## 4. Recursion F1 and Generator F1 — *did it spot the behavioural flags?*

```python
pred = {name for each scope where the flag is true}
gold = {same, from the parser}
→ the same precision / recall / F1
```

**The empty-set convention matters here.** `_prf(∅, ∅)` returns **1.0**: claiming no recursion in a
file that has none is counted as perfect. Across the 20 files, **7 contain no recursive scope at
all**, so 35% of the per-file recursion scores are free.

| flag | your score | scopes in gold | files where the flag never appears |
|---|---|---|---|
| `is_recursive` | **1.0000** | 22 / 416 | 7 / 20 ← free 1.0s |
| `is_generator` | **0.6752** | 46 / 416 | 0 / 20 |

The contrast is informative. Generators appear in every file, so there are no free wins, and the
score drops to 0.675 — `yield` buried inside a nested `try` or loop gets missed. Recursion is rarer
but more visually obvious (a function calling its own name), so when it is present the model gets it.

---

## 5. Relation F1 — *did it get the call graph right?*

```python
triples = {(relation_type, from_name, to_name) for each relation}
→ precision / recall / F1 over those triples
```

A relation only counts as correct if **all three** parts match: a `calls` edge reported where the
truth is `self_recursive` is both a false positive and a false negative.

Edges are only recorded when they resolve to a scope declared in the same file — `len`, `print`
and anything imported are not structure, and counting them would bury the signal.

**Your result: 0.9106**, ranging 0.765 → 0.973 across files. This is the hardest thing the model
does that it still mostly gets right: it must notice a call *and* decide whether it is an ordinary
call, self-recursion, or mutual recursion.

---

## 6. Entrypoint F1 — *did it find what runs the file?*

Set F1 over the names reached from module level or the `if __name__ == "__main__"` guard.

**Your result: 0.0000, then 1.0000.** The zero was not model failure — the sectioner was
swallowing the `__main__` guard into the last function's section, so the module-level prompt never
saw it. After the fix the same file scored 1.000. A metric pinned at exactly 0.000 across every
file is almost always a pipeline bug rather than a model that is uniformly wrong.

---

## 7. Depth MAE and exact rate — *did it count the nesting correctly?*

```python
for each shared name where either depth is non-zero:
    depth_abs   += abs(claimed - truth)
    depth_exact += (claimed == truth)
mae        = depth_abs / n          # average error in levels
exact_rate = depth_exact / n        # share it got exactly right
```

Scopes where **both** depths are zero are skipped, so a flat helper function with no nesting
cannot inflate the score.

**Your result: MAE 0.8437, exact rate 0.4894.** In plain terms: **about half the scopes get the
exact depth, and the typical miss is under one level.** It is not wild — it is systematically
slightly off, which is exactly the profile a prompt correction can fix, and why the
self-improvement loop targets it.

For scale: qwen3:4b multicall had MAE **3.00** on the same kind of file. gpt-oss:120b at 0.84 is a
different regime.

---

## 8. `overall` — the headline

```python
overall = mean(scope_f1, relation_f1, kind_accuracy, parent_accuracy)
```

**It deliberately excludes depth, generators and entrypoints.** It was defined early and is frozen
so that every run in results.md stays comparable against every other. That also means it is
flattered by the three metrics that sit at 1.000 — `overall = 0.9776` while depth exact is 0.4894.

**Quote `overall` for continuity; quote the sub-metrics to describe actual quality.**

---

## 9. `learning_score` — what the training loop optimises

```python
learning_score = mean(scope_f1, relation_f1, kind_accuracy, parent_accuracy,
                      depth_exact_rate, generator_f1, entrypoint_f1)
```

Added when the self-improvement loop was built, because optimising `overall` would have been
pointless: a prompt change that fixed depth perfectly would not move `overall` by a single point.
All seven metrics a prompt change can actually influence, weighted equally.

---

## 10. Schema-valid — *not an accuracy metric*

Separate axis, from `validate_report()`. A record is **valid** when it makes no false claims about
itself: no duplicate ids, no parent pointing at an undeclared scope, no circular parent chain, no
block depth below 1, every relation endpoint declared.

A record can be **100% valid and completely wrong** — the single-call run that returned 1 of 17
scopes was schema-valid. Validity says "this record is internally coherent"; the F1 scores say
"this record is true".

**Errors vs warnings:** errors are facts the record gets wrong about itself and fail it. Warnings
are survivable suspicions — a scope claiming a depth its own blocks do not support, or an
extraction with no blocks enumerated at all. **Your 20-file run: 20/20 valid, 0 errors**, with the
recurring warning being "no blocks enumerated", which is expected since the model is asked for
scopes and relations, not for every block.

---

## 11. Quick reference

| metric | over what | empty-set behaviour | your score |
|---|---|---|---|
| scope F1 | bare names | — | 1.0000 |
| kind accuracy | shared names | 0.0 if no overlap | 1.0000 |
| parent accuracy | shared names, by parent *name* | 0.0 if no overlap | 1.0000 |
| recursion F1 | flagged names | **1.0 when both empty** | 1.0000 |
| generator F1 | flagged names | **1.0 when both empty** | 0.6752 |
| relation F1 | (type, from, to) triples | — | 0.9106 |
| entrypoint F1 | names | **1.0 when both empty** | 1.0000 after fix |
| depth MAE | shared names, non-zero depth | skipped | 0.8437 |
| depth exact | same | skipped | 0.4894 |
| overall | mean of 4 | — | 0.9776 |
| learning_score | mean of 7 | — | loop target |
| schema-valid | the record itself | — | 20/20 |

---

# 12. Error analysis — what the aggregates are made of

An aggregate says *how much* is wrong. This says *what* is wrong. Produced by
`python3 scripts/error_analysis.py`, over **350 scopes in 21 prediction/gold pairs** from the
gpt-oss:120b multicall runs. Re-run it any time; it reads the stored predictions, not a cache.

## 12.1 Depth errors are not random — they are undercounts

| error | scopes | |
|---|---|---|
| −3 levels | 19 | `█████████` |
| −2 levels | 21 | `██████████` |
| **−1 level** | **100** | `██████████████████████████████████████████████████` |
| **exact** | **182** | `████████████████████████████████████████████████████████████` |
| +1 level | 12 | `██████` |
| +2 and above | 16 | `████` |

- **exact 182/350 = 0.5200**
- **undercounts 140 · overcounts 28** — a 5:1 asymmetry
- **mean signed error −0.329**, mean absolute 0.809

This matters more than the headline 0.4894. The model is not guessing — it is **systematically
shaving a level or two off deep nests**, and 100 of the 168 misses are off by exactly one. A
directional bias is correctable by instruction in a way that random noise would not be, which is
why the mined rule states the direction and magnitude rather than just saying "count carefully".

## 12.2 The error is concentrated in deep scopes

| true depth | scopes | exact rate | mean signed error |
|---|---|---|---|
| 1 | 63 | 0.67 | −0.33 |
| 2 | 34 | **0.85** | −0.15 |
| 3 | 35 | 0.63 | −0.37 |
| 4 | 8 | 0.75 | −0.25 |
| 5 | 51 | 0.59 | −0.41 |
| 6 | 8 | **1.00** | +0.00 |
| 7 | 11 | **1.00** | +0.00 |
| 8 | 38 | **0.26** | −1.29 |
| 9 | 13 | 0.31 | −0.54 |
| 10 | 13 | 0.31 | −1.08 |
| 11 | 21 | 0.24 | −0.38 |
| 12 | 10 | 0.30 | −0.10 |
| 13 | 17 | 0.29 | +1.06 |
| 14 | 16 | **0.12** | −1.12 |
| 15 | 6 | 0.17 | −0.83 |

**There is a cliff at depth 8.** Below it the model is right 59–100% of the time; at depth 8 and
beyond it collapses to 12–31%. Counting four or five levels by eye is reliable; counting eleven is
not — the same thing happens to human readers, which is the whole premise of the dataset.

One oddity worth noting: the 6 scopes whose **true depth is 0** got a mean error of **+5.17** —
the model assigns them the nesting of the enclosing function rather than reporting none.

## 12.3 Which constructs it miscounts

Block kinds present in mis-counted scopes versus correctly counted ones:

| block kind | wrong | right | error rate |
|---|---|---|---|
| `while` | 39 | 11 | **0.78** |
| `finally` | 35 | 15 | **0.70** |
| `match` / `case` | 11 | 5 | **0.69** |
| `try` | 72 | 38 | 0.65 |
| `except` | 54 | 30 | 0.64 |
| `for` | 123 | 132 | 0.48 |
| `if` | 157 | 182 | 0.46 |

`for` and `if` — the constructs everyone reads fluently — sit near the 0.48 base rate.
**`try`/`except`/`finally` and `while` are where it goes wrong**, at 0.64–0.78. The likely reason:
an `except` or `finally` is a sibling of the `try` body in the source but *one level deeper* in
Python's AST, and `while` loops in this dataset carry their counter increment inside the body,
which visually flattens them. Those are exactly the cases the mined rule now spells out.

## 12.4 Generator misses are pure recall

| | count |
|---|---|
| missed (was a generator, said no) | **23** |
| invented (said generator, was not) | **0** |

Zero false positives. Every error is a miss, and the most-missed names are
`tracked`, `async_tracked`, `arange` — the context managers and async helpers where the `yield`
sits **inside a `try` block**. That single structural pattern accounts for most of the 0.6752.

## 12.5 Relation errors are also recall-dominated

| relation type | missed | invented |
|---|---|---|
| `calls` | 35 | 11 |
| `yields_from` | 8 | 0 |

3:1 missed-to-invented. The model is conservative: it rarely fabricates an edge, it just fails to
notice some. Combined with 12.4, the picture across every metric is the same — **this model errs
by omission, not by invention.** That is the better failure mode to have, and it tells you where
to push: prompts that encourage completeness, not prompts that demand precision.

## 12.6 What this predicts about the training loop

Three of the four mined rules target exactly what this analysis found: the depth direction
(§12.1), the `try`/`except` nesting convention (§12.3), and `yield` inside nested blocks (§12.4).
If the loop does not move `depth_exact_rate` and `generator_f1`, the hypothesis that these errors
are instruction-correctable is wrong, and the next thing to try is structural — for instance
asking for the block list per scope and computing depth from it, rather than asking for a number.
