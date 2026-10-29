# OPORD → JSON vs Nested Code → JSON

What carried over from the OPORD build, what was dropped, and what is new. Written against the
original source (preserved in `~/.Trash/opord_removed_2026-10-21/`), not from memory.

**One-line summary:** the extraction spine is the same architecture; retrieval was replaced by a
self-generated exemplar, and ground truth plus scoring were promoted into the pipeline itself.
Both the self-improvement loop and retrieval have since been ported, so **every OPORD stage now
has an equivalent** — what differs is the content each one carries, not the shape of the pipeline.

---

## 1. Stage by stage

| # | Stage | OPORD → JSON | Nested Code → JSON | Same? |
|---|---|---|---|---|
| 1 | Load | `_load_opord_text` — .docx via python-docx, .txt | `_load_source` — .py | same role |
| 2 | Context | **RAG**: Chroma over 3 doctrine docs, `get_context(k=6)` | **RAG**: TF-IDF over 3,305 solved train sections, `get_context(k=2)` | **ported** |
| 3 | Ground truth | hand-written gold JSON per example | `gold.py` reads the AST | **new** |
| 4 | Generate | `generate_opord_json` | `generate_code_json` | same |
| 5 | Staged path | `multicall` — 4 fixed passes | `multicall` — N passes, one per definition | same idea |
| 6 | Parse | `extract_json` | `extract_json` — unchanged file | identical |
| 7 | Normalise | `normalize_document` | `normalize_document` | same contract |
| 8 | Validate | `validate_report` | `validate_report` | same contract |
| 9 | Score | separate script, run later | **inline, every run** | **changed** |
| 10 | Persist | SQLite `opord_runs` + `results/preds/` | SQLite `code_runs` + same convention | same |
| 11 | Hierarchy | `to_unit_hierarchy` | `to_scope_hierarchy` + `to_nested_tree` | same + new |
| 12 | Console | webapp, 4 tabs | webapp, 6 tabs | same pattern |
| 13 | Self-improvement | `auto_improve.py` + `learned_hints.py` | `auto_improve.py` + `learned_hints.py` | **ported** |

---

## 2. Modules

### Carried over one-to-one
`config.py` · `llm_client.py` (same `_post_json` / `_chat` / `_ollama_mode` / `_openai_compat_mode`
and the same ollama | groq | openrouter backends) · `new_validators.py` · `pipeline.py` ·
`hierarchy.py` · `logger.py` · `utils.py` · `multicall/sectioner.py` ·
`multicall/segment_prompts.py` · `multicall/merge_partials.py`

### Dropped
| Module | Was | Why it is gone |
|---|---|---|
| `single_command_pipeline.py` + 3 scripts | the per-command classify-then-extract lane | A second task with no code analogue |
| `multicall/context_card.py`, `execution_contract.py`, `support_contract.py` | military concepts (command/support relationships) | Nothing to map onto |
| `battalion_opord_eval.py`, `run_batch_eval.py`, `compare_strategies.py` | offline scoring | Replaced by inline `evaluate.py` + `run_code_pipeline.py` |
| `oporder_worker.py` | Celery worker | Not needed |

### New
| Module | Does |
|---|---|
| `app/gold.py` | AST ground truth — scopes, blocks, relations, self/mutual recursion, depth per scope |
| `app/evaluate.py` | Set arithmetic over names: scope F1, kind, parent, relation F1, depth MAE |
| `scripts/generate_nested_code.py` | Generates the dataset: 13 nesting templates, measured and floor-checked |
| `scripts/deploy_gpu.sh` | inspect / push / setup / run / pull against the GPU box |
| `app/learned_hints.py` | working memory: rules + corrected examples read by both prompt builders |
| `scripts/auto_improve.py` | mines failures, keeps a version only if it beats the held-out split |

---

## 3. The schema shrank by a factor of four

| | OPORD | Code |
|---|---|---|
| Top-level keys | **19** — `classification`, `echelon`, `doctrine_source`, `metadata`, `terrain`, `situation`, `mission`, `phases`, `grouping`, `locations`, `control_measures`, `tasks`, `coordinating_instructions`, `fires`, `sustainment`, `command_and_signal`, `annotations`, … | **5** — `file_id`, `scopes`, `blocks`, `relations`, `entrypoints` |
| Lexicon groups | **13** — echelons, unit_types, task_verbs, task_types, relation_types, time_kinds, location_types, control_measure_types, support_roles, … | **6** — scope_kinds, block_kinds, relation_types + 3 alias maps |

The OPORD schema is wide because an order says many *kinds* of thing. A code record is narrow and
deep: few entity types, but they nest arbitrarily. That difference drives everything below.

---

## 4. The hierarchy view: same join, different axis

`to_unit_hierarchy` and `to_scope_hierarchy` are the same function with the nouns swapped.

| OPORD | Code |
|---|---|
| unit | scope (module / class / function / method) |
| **phase** — the ordered axis work is laid out along | **nesting depth** — the ordered axis |
| `ALL_PHASES` bucket for records naming no phase | `ANY_DEPTH` bucket for blocks with no depth |
| grouping: standing facts + relations, both sides | structure: standing facts + relations, both sides |
| tasks bucketed by phase | blocks bucketed by depth |
| units sorted parents-before-children (chain of command) | scopes sorted parents-before-children (lexical nesting) |
| `unassigned` for tasks naming an undeclared unit | `unassigned` for blocks naming an undeclared scope |

**New in the code build:** `to_nested_tree` — a real recursive tree (one root, scopes inside
scopes, blocks inside blocks, nested defs placed where they are defined). The OPORD view never had
this, because a chain of command is shallow and a program is not.

---

## 5. Multicall: fixed stages vs file-driven

| | OPORD | Code |
|---|---|---|
| Passes | **4, fixed** — sectioner, situation/mission, execution, support | **N, variable** — one per top-level `def`/`class`, plus module header and trailer |
| Split on | document headings | column-zero `def` / `async def` / `class` / `@` |
| Typical count | 4 | 11–24 |
| Merge | onto the full schema template, then heal references | onto a record template, then type relations (self / mutual recursion) |

Same reasoning in both: one request cannot hold a long input *and* its full answer, so sections get
their own request and the merger starts from a complete template so no key can go missing.

---

## 6. Evaluation: the biggest difference

| | OPORD | Code |
|---|---|---|
| Gold source | **hand-written** JSON per example | **derived from the AST**, free, exact |
| Gold coverage | 6 example orders | all 1000 samples |
| When scored | separately, afterwards (`battalion_opord_eval.py gold_json pred_json`) | **inline, in every run** |
| Metrics | mission / task / unit field accuracy | scope F1, kind accuracy, parent accuracy, relation F1, recursion F1, generator F1, entrypoint F1, depth MAE |
| Annotation cost | a human per document | zero |

This is the one place the code domain is strictly better off: the parser already knows the right
answer, so there is no annotation bottleneck and no gold-coverage ceiling.

---

## 7. Data

| | OPORD | Code |
|---|---|---|
| Source | real battalion orders (.docx) | **generated** by `generate_nested_code.py` |
| Volume | 6 worked examples | 1000 programs, 843,965 lines |
| Control over difficulty | none — you get what the orders contain | depth floor enforced by measurement; nothing shallow survives |
| Splits | ad hoc | train 800 / val 100 / test 100 |

---

## 8. Storage and UI

**`code_runs` adds three columns** over `opord_runs` (`doc_id`→`file_id`, `model_name`,
`json_output`, `is_valid`, `validation_errors`, `validation_warnings`, `created_at`):
`score`, `overall`, `elapsed_s` — because scoring is now part of the run.

**Per-run artefacts.** OPORD wrote `pred.json` + `report.json`. The code build adds
`tree.json`, `hierarchy.json`, `tree.txt`, `gold.json`, `gold_tree.json`, `gold_hierarchy.json`.

**Console tabs.** OPORD: Single command · Full OPORD · Evaluation · History.
Code: Overview (documentation + architecture diagram) · Dataset · Extract · Hierarchy
(Diagram / Indented / Flat / ASCII / JSON) · Evaluation · History.

---

## 9. What stayed identical in spirit

- **Save-and-mark** — validation never blocks a write; a failed extraction is evidence.
- **Normalise before judging** — say the answer in the lexicon's words first, so a correct answer
  is not failed for spelling (`occupies`→`occupy` there, `def`→`function` here).
- **Errors vs warnings** — errors are facts the record gets wrong about itself; warnings are
  survivable suspicions.
- **Dangling references are kept, not dropped** — a reference to something undeclared is a real
  finding, so the view agrees with the validator that reports it.
- **Flat storage, joined for reading** — every fact in exactly one place; the hierarchy join
  duplicates deliberately, for a reader.


---

## 10. The self-improvement loop (ported 2026-10-22)

Same shape as the OPORD original, different content — because what a code extraction gets wrong
is different. Scope, kind, parent and recursion are already at 1.000, so there is nothing to learn
there; the loop goes after **nesting depth**, the **generator flag**, and **invented or missed
call edges**.

| | OPORD | Code |
|---|---|---|
| Working memory | `assets/eval/learned_hints.json` | same path, same file |
| Read by | the single-command prompts | `llm_client.build_prompt` **and** `segment_prompts.build_section_prompt` |
| Mined from | failed field comparisons | per-scope depth deltas, generator-flag mismatches, relation set differences |
| Rules written | per bucket | direction + magnitude of the depth error, elif/except nesting, what counts as a call |
| Examples | corrected command + expected JSON | the real source slice of the worst-missed scope + its true depth and block kinds |
| Acceptance | strictly better on a held-out split | identical — a tie is a rejection |
| Disable | `LEARNED_HINTS=0` | identical |

**Why a new metric.** `overall` is the mean of scope F1, relation F1, kind and parent accuracy —
it does not include depth, which is exactly what the loop is trying to fix, and it is frozen so
earlier runs stay comparable. So `aggregate()` gained `learning_score`: the mean of all seven
metrics a prompt change can actually move (scope F1, relation F1, kind, parent, depth exact rate,
generator F1, entrypoint F1). The loop optimises that.

**Token budget.** The staged path sends one request per definition, so a full set of worked
examples on every section would cost more than the correction is worth. Section prompts get the
rules plus one example; the single-call prompt gets all three.

```bash
python3 scripts/auto_improve.py --rounds 2 --dev 10 --test 10
python3 scripts/auto_improve.py --report-only
```


---

## 11. Retrieval (ported 2026-10-22)

The OPORD build retrieved **doctrine**, because the meaning of an order lives in documents
outside it. Code has no doctrine — but it has something an order never had: 800 training files
whose correct answer is already known exactly, from the parser. So the corpus is **worked
examples**: given the section being extracted, retrieve the most similar sections that are
already solved, and show the model those solutions.

| | OPORD | Code |
|---|---|---|
| Corpus | 3 doctrine markdown files | 3,305 sections from 250 train files |
| Chunk | a passage of doctrine | a definition's source + its AST-gold answer |
| Embedding | sentence-transformers → Chroma | TF-IDF over code identifiers, inverted index |
| API | `get_context(query, k=6, rebuild)` | `get_context(query, k=2, rebuild, exclude_file_id)` |
| Diversity pass | `_pick_diverse` | `_pick_diverse` — skips examples of the same kind *and* depth |
| Disable | — | `RAG=0` |
| Build | `rebuild_vectorstore.py` | `rebuild_vectorstore.py` |

**Leakage is the thing that matters here.** A val or test file appearing in the corpus would leak
its own answer into its own extraction and make every number afterwards meaningless. Two guards:
`build_index` filters on the manifest's `split == "train"`, and `get_context` additionally drops
any chunk from the file being extracted. Verified: 0 non-train chunks in the index.

**Why TF-IDF rather than embeddings.** The GPU box has no working pip (no `python3-venv`), and
the rest of this pipeline has no dependencies at all. Lexical similarity over identifiers works
well here because the corpus is structurally repetitive — a query for a branch-ladder function
returns branch-ladder functions. `_vector()` in `rag_store.py` is the single swap point for
neural embeddings; nothing else would change.

```bash
python3 scripts/rebuild_vectorstore.py --limit 250
RAG=0 python3 scripts/run_code_pipeline.py --count 20   # no-retrieval baseline
```
