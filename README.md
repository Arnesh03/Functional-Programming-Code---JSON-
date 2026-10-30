# Nested Code → JSON

Read one Python file, report its **structure** as JSON: every scope (module, class,
function, method), the control-flow blocks inside each, and the relations between them —
calls, self-recursion, mutual recursion, inheritance.

The architecture is a port of an OPORD→JSON extraction pipeline, pointed at code. The
stages are the same; what changed is that **code comes with its own answer key**. A Python
file's ground truth can be read straight out of the AST, so every run is scored as it
happens, with no annotation step and no gold-coverage ceiling.

```bash
python3 main.py extract nested_00002 --strategy multicall   # one file through the model
python3 main.py extract nested_00002 --gold                 # ground truth, no model
python3 main.py tree    nested_00002                        # the nested structure
python3 scripts/run_code_pipeline.py --count 20             # batch, with scoring
python3 webapp/server.py                                    # the console, localhost:8000
```

---

## Results

20 files, `gpt-oss:120b`, multicall, 4 × H200 — 46.2 min, **20/20 schema-valid**, 0 failures.

| metric | score |
|---|---|
| scope F1 · kind · parent · recursion | **1.0000** each |
| relation F1 | 0.9106 |
| generator F1 | 0.6752 |
| depth exact rate | **0.4894** |
| overall | **0.9776** |

Scope F1 is 1.000 on *every individual file* — in 800-line programs nested 16 levels deep,
every module, class, function and method found, with no invented scopes.

**Read [`docs/metrics.md`](docs/metrics.md) §5a before quoting the four 1.000s.** Two of them
are partly artifacts of the pipeline rather than model skill: the prompt carries the roster of
top-level names, and 67% of scopes are module-level where the merger supplies the parent by
default. The honest signal is the low scores — depth exact 0.489 and generator F1 0.675 are
computed the same way and are poor, which is what a working measurement looks like.

Full record of every run: [`docs/results.md`](docs/results.md).

For the project end to end in prose — the problem, the dataset, the schema, the results and
their caveats — read [`docs/walkthrough.md`](docs/walkthrough.md). To present it, the deck is
at [claude.ai/artifact/5NupPBxKAWfPUkdtVypZUH](https://claude.ai/artifact/5NupPBxKAWfPUkdtVypZUH)
and [`docs/presenting-the-deck.md`](docs/presenting-the-deck.md) explains all 28 slides.

---

## The dataset

`scripts/generate_nested_code.py` generates nesting **to order**, because scraped corpora do
not contain it. Measured over 3,001 real py150 files: 45% have no nesting at all, and only
0.27% reach depth 14.

| | |
|---|---|
| programs | 1,000 |
| lines | 843,965 (mean 844) |
| measured block depth | 10–16, every file |
| recursion-in-recursion / mutual | 390 files each |
| rejected below floor · duplicates | 0 · 0 |
| parse, compile and execute | 1,000 / 1,000 |

Thirteen nesting templates: loop pyramids, if/elif ladders, try/except/finally stacks, context
managers, nested comprehensions, closure towers, inner classes, self/nested/mutual recursion,
async, match/case, generators, state machines, deep literals.

```bash
python3 scripts/generate_nested_code.py --count 1000 --run-check 25 --clean
```

Depth is a **guarantee**, not an intention: every file is re-parsed and measured after
generation, and anything shallower than the floor is discarded and regenerated.

---

## Pipeline

```
load → gold (AST truth) → retrieval → LLM → parse → normalise → validate → score → store → render
```

| module | does |
|---|---|
| `app/gold.py` | ground truth from the AST — scopes, blocks, relations, recursion, depth |
| `app/llm_client.py` | ollama · groq · openrouter behind one dispatcher |
| `app/multicall/` | one request per top-level definition, merged onto a complete template |
| `app/rag_store.py` · `retriever.py` | retrieval over already-solved train-split sections |
| `app/new_validators.py` | normalise against the lexicon, then validate shape and semantics |
| `app/evaluate.py` | scope F1, kind, parent, relation F1, depth MAE — scored inline |
| `app/hierarchy.py` | flat scope view, plus a true nested tree |
| `app/learned_hints.py` · `scripts/auto_improve.py` | self-improvement with a held-out gate |

**Single call vs multicall.** On an 850-line file a single request returned **1 of 17 scopes**
(F1 0.111): the model spent its whole context reading and had nothing left to answer with.
Splitting on top-level `def`/`class` took the same model to **0.938**.

Two conventions decide what the right answer is, and both follow Python's own AST: an `elif`
nests one level inside its `if`, and an `except`/`else`/`finally` one level inside its `try`.

---

## Self-improvement, and why it was rejected three times

`scripts/auto_improve.py` mines failures into prompt rules and corrected examples, then keeps a
version **only if a held-out split strictly improves**. A tie is a rejection.

| run | corpus | dev | held-out | verdict |
|---|---|---|---|---|
| 1 | generated | **+0.065** | **−0.032** | real memorisation, caught |
| 2 | CodeComplex | +0.0008 | −0.0136 | inside the noise |
| 3 | CodeComplex, depth rules only | −0.0127 | −0.0005 | inside the noise |

Run 1 is the gate earning its keep: measured on dev alone it would have read as a 6.5-point
success and shipped a regression.

Runs 2 and 3 exposed something more useful. Two runs with the **same seed and the same files**
produced baselines differing by up to 0.049 on depth exact rate — so the measurement floor is
roughly ±0.011, and effects smaller than that cannot be resolved. Before any further prompt
experiments: greedy decoding, more files per split, and a repeated baseline.

---

## Layout

```
app/        the pipeline
scripts/    generator, batch runner, auto_improve, error_analysis, deploy_gpu
assets/     schema, lexicon, retrieval index, learned hints
data/       the generated dataset (1,000 programs + manifest + stats)
docs/       walkthrough.md · presenting-the-deck.md · results.md · metrics.md
            architecture-diff.md · architecture.svg
webapp/     stdlib-only console: six tabs, five hierarchy views
```

`DATASET_DIR` selects the corpus, so several datasets coexist:

```bash
DATASET_DIR=data/codecomplex python3 scripts/run_code_pipeline.py --count 20
RAG=0 LEARNED_HINTS=0 python3 scripts/run_code_pipeline.py --count 20   # ablation
```

---

## Datasets not included here

**py150** is AST-only — it ships no source text, so it cannot feed this pipeline at all. It is
used once, in `scripts/build_nested_code_dataset.py`, to measure how shallow real code is.

**CodeComplex** (4,900 Codeforces submissions) declares no licence, so it is not redistributed:

```bash
curl -L -o python_data.jsonl \
  https://raw.githubusercontent.com/sybaik1/CodeComplex/main/data/python_data.jsonl
python3 scripts/build_codecomplex_dataset.py
```

Worth knowing before you reach for it: it is real but **shallow** — median 24 lines, and only
22 of 4,900 files reach depth 8. It tests generalisation to real code, not deep nesting.

---

## Requirements

Python 3.10+. The pipeline is **stdlib-only**; `python-dotenv` is optional. An LLM backend is
needed only for model runs — `--gold` exercises every other stage without one.
