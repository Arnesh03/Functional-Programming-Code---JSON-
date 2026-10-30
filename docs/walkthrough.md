# Nested Code → JSON

Arnesh Singh · 30 October 2026 · [the deck](https://claude.ai/artifact/5NupPBxKAWfPUkdtVypZUH) · [slide-by-slide guide](presenting-the-deck.md)

This project reads a Python file and writes down its structure — every function and class, the loops and branches inside each, and how they call one another — then checks that answer against what the Python parser already knows. On 20 files of roughly 850 lines each, nested up to 16 levels deep, it finds every scope correctly; where it struggles is counting how deep the nesting goes.

## The problem

Give the system one Python file. It gives back a structured description of that file — not a summary of what the code *means*, but an index of its *shape*.

Three lists come out:

1. **Scopes** — every namespace in the file: the module itself, then each class, function and method. For each one: its name, what kind it is, which scope it sits inside, whether it calls itself, whether it yields, and how deeply nested its body goes.
2. **Blocks** — every control-flow construct inside those scopes: each `for`, `while`, `if`, `try`, `with`, `match`. For each one: its kind, which block encloses it, and its depth.
3. **Relations** — the edges between scopes: who calls whom, which functions recurse, which call each other in a cycle, which class inherits from which.

So for a small function that walks a tree and calls itself, the answer records that it is a function, that it lives at module level, that it is recursive, that its deepest nesting is four levels, and that it uses `for`, `if`, `else`, `try` and `except`.

The useful way to think about it: the system is building a map of a program's skeleton, in a form a machine can read.

## Why nesting is the hard part

Most of the job is easy. Listing the functions in a file is close to reading them off the page. Saying whether something is a function or a method is a matter of where the `def` sits.

Counting how deep the nesting goes is not easy, and there are two reasons why.

**First, deep nesting overwhelms the eye.** A loop inside a loop inside a `while` inside a `try` inside an `if` is eleven levels by the time the ladder finishes. A person counts indents to answer that. A language model answers from impression, and impressions get worse the deeper you go.

**Second, two of Python's rules are counter-intuitive.** They decide what the correct answer actually is:

- An `elif` is **one level deeper** than the `if` above it. On the page the two look like siblings. Internally Python treats `elif` as a fresh `if` nested inside the previous one's `else`.
- An `except`, `else` or `finally` is **one level deeper** than its `try`, for the same reason.

So this fragment is four levels deep, not two:

```python
for row in matrix:          # 1
    if value > 0:           # 2
        pass
    elif value < 0:         # 3  (nested inside the if)
        pass
    else:                   # 4  (nested inside the elif)
        pass
```

This matters for the whole project, because every number reported later depends on which convention is used. The project follows Python's own parser, so its figures agree with the language rather than with intuition.

## Where the design came from

This is not a system built from nothing. It reuses the architecture of an earlier project that turned military operations orders — OPORDs — into structured JSON. The stages are the same; only the nouns changed.

| In the orders project | Here |
| --- | --- |
| a unit | a scope (module, class, function, method) |
| the phase of an operation | the nesting depth |
| the chain of command | lexical nesting |
| command and support relationships | calls and recursion |
| `occupies` folded to `occupy` | `def` folded to `function` |

Ten modules carried over, several unchanged. The file that pulls JSON out of a model's reply is byte-for-byte the same file.

### The one idea that makes this project work

An operations order needs a human to write down its correct answer. Somebody reads the document and records what it says, which is slow, so that project had **six** annotated examples.

A Python file does not have that problem. **The parser already knows the answer.** Running Python's own `ast` module over the file produces the exact list of scopes, blocks and relations — for free, in milliseconds, with nobody annotating anything.

That single difference changes what is possible:

- Ground truth exists for **all 1,000** files instead of a handful.
- Scoring moves *inside* the pipeline. Every run is graded the moment it finishes, rather than in a separate exercise weeks later.
- There is no annotation bottleneck capping the size of the evaluation set.

If your guide asks what is novel here, this is the honest answer: not the architecture, which is borrowed, but the fact that the task supplies its own answer key and the system was built to exploit that.

## Step 1 — Building the dataset

The system is meant to be tested on deeply nested code. The first question is where to get it.

### Why not just download real code?

The obvious move is to take a public corpus of Python. I measured what that actually gives you, using 3,001 real files from the py150 corpus:

*Figure — py150 nesting depth over 3,001 real Python files, measured with this project's own parser. Shown as a bar chart on slide 7 of the deck; the underlying numbers are in the appendix below.*

Real Python is overwhelmingly flat. **Forty-five percent of files have no nesting whatsoever.** At that rate the entire 150,000-file corpus holds roughly 400 files nested 14 levels deep, and the project needed a thousand.

So a scraped corpus cannot supply the test set. It has to be generated.

### What was generated

|  |  |
| --- | --- |
| programs | 1,000 |
| total lines | 843,965 (mean 844 per file) |
| measured nesting depth | 10 to 16, every file |
| files with recursion inside recursion | 390 |
| files with mutual recursion | 390 |
| files that parse, compile and run | 1,000 of 1,000 |

Each program is assembled from **13 nesting templates** — loop pyramids, if/elif ladders, try/except/finally stacks, context managers, nested comprehensions, closures inside closures, classes with inner classes, three kinds of recursion, async code, `match`/`case`, generators, state machines and deeply nested data. Every file is real, working Python: all 1,000 were executed to completion as a check.

### Depth is a guarantee, not an intention

This is the part worth defending. The generator does not *assume* its templates produce deep nesting — it **measures** every file after writing it, using the same parser that produces ground truth. Anything shallower than the floor is thrown away and generated again.

On the build that produced this dataset: **0 files rejected, 0 duplicates.** The templates cleared the floor on the first attempt every time.

### The fair criticism, stated plainly

Generated code is more regular than human code. Names follow a pattern, structures repeat, and there are no messy real-world habits. That makes some parts of the task easier than they would be on a real codebase, and your guide may well raise it.

The project answers it in Step 6 by running the same pipeline over real Codeforces submissions and comparing.

## Step 2 — The pipeline

The same file goes down two paths. The green path is the parser working out the right answer. The lower path is the model attempting it. They meet at the score.

*Figure — the pipeline: 8 stages, two paths that meet at the score. Drawn as [docs/architecture.svg](architecture.svg), and as slide 8 of the deck.*

The green path runs **first**, before the model is asked anything — so the answer is already known when the attempt arrives, and the score is computed in the same run rather than in a separate exercise later.

Two details worth knowing about stage 3. The file is **split on top-level `def` and `class` lines** and each definition is sent as its own request. This matters: an early version sent the whole 850-line file in one request and got back **1 scope out of 17** — the model spent its entire context window reading and had nothing left to answer with. Splitting it took the same model from 0.111 to 0.938 on the same file.

Stage 4 is vocabulary, not meaning. If the model writes `def` where the schema says `function`, or `catch` where it says `except`, that is a correct answer in the wrong words — so the wording is normalised **before** anything is judged.

## The JSON shape — every key, and what it holds

This is the contract. The model is asked for exactly this shape, the parser produces exactly this shape, and the scorer compares one against the other key by key. It is written down formally in `assets/schema/nested_code_schema_v1.json`.

One Python file becomes **one JSON object with five top-level keys**:

| key | type | holds | required |
| --- | --- | --- | --- |
| `file_id` | string | the file's name, normally its stem | yes |
| `scopes` | array of objects | every namespace: the module, each class, function, method, lambda | yes |
| `blocks` | array of objects | every control-flow block, and which block encloses it | gold always; optional from the model |
| `relations` | array of objects | the edges between scopes — who calls whom, who recurses, who inherits | yes |
| `entrypoints` | array of strings | the `scope_id`s reached from module level or the `__main__` guard | no |

### `scopes[]` — 14 keys per namespace

| key | type | what it means |
| --- | --- | --- |
| `scope_id` | string | dotted path from the module, e.g. `module.Ledger42.tally` |
| `name` | string | the bare name — `tally`. **This is the key the scorer matches on** |
| `kind` | enum | `module` · `class` · `function` · `async_function` · `method` · `async_method` · `lambda` · `comprehension` |
| `parent_id` | string | the `scope_id` of the enclosing scope; empty string for the module |
| `is_async` | boolean | declared with `async def` |
| `is_recursive` | boolean | the scope calls its own name |
| `is_generator` | boolean | the scope contains a `yield` |
| `decorators` | array of strings | `["contextmanager"]`, `["staticmethod"]` … |
| `params` | array of strings | the parameter names, in order |
| `start_line` | integer | first line of the definition |
| `end_line` | integer | last line of its body |
| `max_block_depth` | integer | the deepest chain of control-flow blocks inside it, counting from 1 |
| `block_kinds` | array of strings | the distinct constructs used inside it, e.g. `["if", "try", "finally"]` |

Only three of those are mandatory: `scope_id`, `name`, `kind`.

### `blocks[]` — 7 keys per control-flow block

| key | type | what it means |
| --- | --- | --- |
| `block_id` | string | `b0001`, `b0002`, … |
| `scope_id` | string | which scope this block lives in |
| `kind` | enum | `for` · `async_for` · `while` · `if` · `try` · `with` · `async_with` · `match` · `case` · `except` · `finally` · `else` |
| `parent_block_id` | string | the enclosing block; empty string when the block sits directly in the scope body |
| `depth` | integer | nesting level **within its scope**, starting at 1 — this resets inside every nested `def` |
| `line` | integer | the line the block opens on |
| `test` | string | a short rendering of the condition or loop target, e.g. `len(log) < 64` |

Mandatory: `block_id`, `scope_id`, `kind`, `depth`.

### `relations[]` — 5 keys per edge

| key | type | what it means |
| --- | --- | --- |
| `relation_id` | string | `r0001`, `r0002`, … |
| `relation_type` | enum | `calls` · `self_recursive` · `mutually_recursive` · `inherits` · `closes_over` · `yields_from` |
| `from_scope` | string | the scope the edge leaves |
| `to_scope` | string | the scope it arrives at |
| `notes` | string | free text, usually empty |

Mandatory: all but `notes`.

### A real record, trimmed

Straight out of `results/preds/nested_00002_D14_L9_B9/gold.json`:

```json
{
  "file_id": "nested_00002_D14_L9_B9",
  "scopes": [
    {
      "scope_id": "module.tracked",
      "name": "tracked",
      "kind": "function",
      "parent_id": "module",
      "is_async": false,
      "is_recursive": false,
      "is_generator": true,
      "decorators": ["contextmanager"],
      "params": ["label", "log"],
      "start_line": 22,
      "end_line": 30,
      "max_block_depth": 3,
      "block_kinds": ["if", "try", "finally"]
    }
  ],
  "blocks": [
    {
      "block_id": "b0001",
      "scope_id": "module.tracked",
      "kind": "if",
      "parent_block_id": "",
      "depth": 1,
      "line": 24,
      "test": "len(log) < 64"
    }
  ],
  "relations": [
    {
      "relation_id": "r0001",
      "relation_type": "calls",
      "from_scope": "module",
      "to_scope": "module.pipeline_00002",
      "notes": ""
    }
  ],
  "entrypoints": ["module.pipeline_00002"]
}
```

That one file produced 18 scopes, 260 blocks and 11 relations in full.

### When a key is missing or misspelled

`normalize_document()` in `app/new_validators.py` repairs the shape before anything is judged, so a model that omits a key is not punished for formatting:

- any of the four arrays missing → becomes `[]`
- `scope_id` missing → falls back to `name`
- `kind` missing on a scope → defaults to `function`
- `block_id` or `relation_id` missing → generated as `b0001` / `r0001`
- numbers arriving as strings, or absent → coerced to integers, 0 if unusable
- `is_async` is forced true whenever `kind` begins with `async`

And every `kind` and `relation_type` is folded through `assets/lexicon/nested_code_lexicon_v1.json`, which maps about 60 synonyms onto the canonical words — `def` and `func` to `function`, `staticmethod` and `classmethod` to `method`, `foreach` to `for`, `catch` to `except`, `switch` to `match`, `invokes` to `calls`, `indirect recursion` to `mutually_recursive`. A value it does not recognise is left alone, for the validator to flag.

### Two further JSON files are derived from the record

`app/hierarchy.py` re-joins the flat record into two readable views, each with its own keys.

**`*_hierarchy.json`** — blocks bucketed by depth: `file_id`, `depths`, `depth_labels`, `entrypoints`, `scopes`, `unassigned`. Each scope inside it repeats the record's fields and adds `signature`, `structure` and `scope_nesting`.

**`*_tree.json`** — the real recursive tree: `file_id`, `entrypoints`, `totals` (`scopes`, `blocks`, `max_depth`, `relations`) and `root`. Every node carries `id`, `node_type` (`scope` or `block`), `kind`, `name`, `label`, `flags`, `params`, `decorators`, `start_line`, `line`, `end_line`, `max_block_depth`, `block_kinds`, `relations`, `counts` and `children` — so a block node sits inside the scope node it belongs to, and nesting in the JSON mirrors nesting in the code.

These two are presentation, not ground truth. Scoring only ever reads the five-key record.

## Step 3 — How the scoring works

The model's answer and the parser's answer are both lists. Scoring compares them.

**Matching is done on plain names, not on identifiers.** Two records can describe the same file correctly and still disagree on whether a path is written `module.Counter.tally` or `Counter.tally`. Penalising that would measure whether the model followed the prompt's formatting, not whether it understood the code.

There are three different kinds of comparison:

| metric | question it answers | how it is computed |
| --- | --- | --- |
| scope F1 | Did it find the right set of functions and classes? | overlap between the two name sets |
| kind accuracy | Did it label each one correctly? | share of agreed names with the same kind |
| parent accuracy | Did it put each one in the right place? | share of agreed names with the same parent |
| relation F1 | Did it get the call graph right? | overlap of (type, caller, callee) triples |
| recursion F1 | Did it spot which functions recurse? | overlap of the flagged name sets |
| generator F1 | Did it spot which functions yield? | overlap of the flagged name sets |
| depth MAE | How far off is the nesting count? | average error, in levels |
| depth exact rate | How often is the count exactly right? | share that match exactly |

### Two composite numbers

`overall` is the average of scope F1, relation F1, kind and parent accuracy. It was defined early and frozen, so every run in the project stays comparable. **It deliberately leaves depth out.**

`learning_score` is the average of all seven metrics a prompt change could move, depth included. It was added later, for the improvement experiments in Step 6 — because optimising `overall` would have been pointless when a change that fixed depth perfectly would not move it by a single point.

### Being valid is not the same as being right

There is a separate check that asks whether a record contradicts *itself*: ids used twice, a parent that was never declared, a loop in the parent chain, a relation pointing at nothing.

A record can pass that check completely and still be badly wrong. One early run returned **1 scope out of 17** and was perfectly valid, because everything it did say was internally consistent. Validity means coherent. The F1 scores mean true.

## Step 4 — The results

Main evaluation: **20 files**, model `gpt-oss:120b`, running on four NVIDIA H200 GPUs. 46.2 minutes, **20 of 20 records schema-valid**, no failures.

| metric | score |
| --- | --- |
| scope F1 | 1.0000 |
| kind accuracy | 1.0000 |
| parent accuracy | 1.0000 |
| recursion F1 | 1.0000 |
| relation F1 | 0.9106 |
| generator F1 | 0.6752 |
| depth exact rate | 0.4894 |
| depth MAE | 0.84 levels |
| **overall** | **0.9776** |

Shading in the tables throughout: **green** a strong result, **amber** weak, **red** poor or not trustworthy, **blue** the headline figure, **grey** no measurable effect.

### Reading this honestly

The headline is genuine: in 800-line programs nested 16 levels deep, **every** module, class, function and method was found, on **every** file, with nothing invented. That is not an average hiding bad cases — scope F1 is 1.000 on each file individually.

But four of those scores are exactly 1.000, and that should make anyone suspicious. Step 5 explains which of them are flattered and why.

### Where the remaining error actually lives

Three numbers are below 1.000, and they are the interesting ones:

- **depth exact rate 0.4894** — about half the scopes get the depth exactly right. This is the real weak point.
- **generator F1 0.6752** — a `yield` buried inside a `try` block gets missed.
- **relation F1 0.9106** — occasionally a call edge is missed or invented.

An analysis of 350 individual scopes found the depth errors are not random:

- **140 undercounts against 28 overcounts**, a 5-to-1 bias. The model consistently shaves a level off.
- **100 of the 168 misses are off by exactly one.**
- There is a **cliff at depth 8**: below it the model is right 59–100% of the time; at depth 8 and beyond it falls to 12–31%.
- The constructs it gets wrong are `while` (78% error), `finally` (70%), `try` (65%) and `except` (64%) — against `for` (48%) and `if` (46%).

That last line matters: `try`/`except`/`finally` are exactly the constructs with the counter-intuitive nesting rule from earlier.

*Figure — error analysis over 350 scopes across 21 prediction/gold pairs. Shown on slides 13 and 14 of the deck; the per-construct numbers are in [docs/results.md](results.md).*

The shape is the argument. Up to seven levels the model is mostly right; from eight levels on it is mostly wrong. Counting four nested blocks by eye is reliable, counting eleven is not — which is exactly the difficulty the dataset was built to create.

## Step 5 — Why four scores are exactly 1.000

A perfect score should always invite suspicion. I checked each one rather than reporting it as-is. Two are partly artifacts of the pipeline itself, not model skill.

### scope F1 — the model is shown the name list

Each prompt includes the roster of top-level names in the file, because it is needed so that calls between sections can be resolved. The side effect is that the model is **confirming** names rather than discovering them.

*What is still genuine:* 136 of the 416 scopes (33%) are nested inside others — methods and inner functions the roster never mentions — and those were all found too, with nothing invented.

### parent accuracy — two-thirds of it is a default

67% of scopes sit at module level, and the merging code fills in `"module"` automatically whenever the model gives no parent. So for two-thirds of the scopes the "correct" answer is supplied by the pipeline, not chosen by the model. The real question is only asked on the other 136.

### recursion F1 — seven files score it for free

Comparing an empty set against an empty set counts as perfect. Across the 20 files there are only 22 recursive scopes out of 416, and **7 files contain none at all** — so 35% of the per-file scores are free marks.

*What is still genuine:* on the 13 files that do contain recursion, it was identified correctly, including recursion inside recursion and mutual recursion.

### kind accuracy — the task is simply easy

Deciding between module, class, function and method is nearly mechanical: a `def` at the left margin is a function, a `def` inside a `class` is a method. 1.000 is the expected result, not a surprising one.

### Why the measurement can still be trusted

This is the argument to make if challenged. **Depth exact rate 0.4894 and generator F1 0.6752 are computed the same way, by the same code, and they are poor.**

If the metrics were broken or the task were trivial, everything would read high. Easy things scoring high while the genuinely hard thing scores low is exactly what a working measurement looks like.

## Step 6 — Trying to make it better

Depth is the weak point, so the next question is whether it can be fixed by telling the model how to count.

### How the improvement loop works

Worth being precise about the vocabulary: **nothing is trained in the machine-learning sense.** No weights change, there are no gradients. What improves is the *prompt's working memory* — a file of rules and corrected examples the prompt reads.

Each round:

1. Score a **dev** split of files.
2. Mine the failures into rules and corrected examples — e.g. “you are undercounting by 0.8 levels on average; count the longest chain by following the indentation”, plus the real source of three badly-missed functions with their true depths.
3. Score the dev split again with those hints in place.
4. Score a **held-out** split that was never used for mining.
5. Keep the new hints **only if the held-out score strictly improves**. A tie counts as a rejection.

Step 5 is the safeguard. Because the examples are taken *from* the dev files, improving on dev is partly just memorising them. Only the untouched split can show whether anything generalised.

### Three runs, three rejections

| run | corpus | dev change | held-out change | verdict |
| --- | --- | --- | --- | --- |
| 1 | generated | **+0.065** | **−0.032** | memorisation, caught |
| 2 | real code (CodeComplex) | +0.0008 | −0.0136 | no effect |
| 3 | real code, depth rules only | −0.0127 | −0.0005 | no effect |

**Run 1 is the gate earning its keep.** The hints improved the files they were mined from by 6.5 points and made everything else *worse* by 3.2 points. Four of six held-out files got worse, one by 24 points. Measured on dev alone, this would have been written up as a clear success — and a regression would have shipped.

### A useful side result

Runs 2 and 3 used real Codeforces submissions instead of generated files. That comparison answered the fairness question from Step 1:

|  | generated (deep) | real code (shallow) |
| --- | --- | --- |
| median lines | 844 | 24 |
| files at depth 8 or more | 1,000 of 1,000 | 22 of 4,900 |
| depth exact rate | 0.49 | 0.79–0.84 |

**Difficulty tracks depth, not artificiality.** The model does far better on shallow real code than on deep generated code — so the generated dataset is hard for the right reason, because the nesting is deep, not because it is synthetic. That is an argument you could not make without the real-code comparison.

## Step 7 — The measurement-noise finding

This is the most important methodological result, and it came out of a failure.

Runs 2 and 3 used **the same random seed**, so they drew **the same 20 dev files and the same 20 held-out files**. Their baselines — the score before any hints are applied — should have been identical. They were not:

| baseline metric | run 2 | run 3 | difference |
| --- | --- | --- | --- |
| learning score, dev | 0.9565 | 0.9672 | +0.0107 |
| overall, held-out | 0.9670 | 0.9490 | −0.0180 |
| depth exact rate, dev | 0.8380 | 0.8870 | **+0.0490** |

Same files, same code, same model, different numbers — purely because the model samples its output rather than producing one fixed answer (`temperature = 0.2`).

**So the measurement floor is roughly ±0.011 on the composite, and up to ±0.05 on depth.**

Now compare that with the effects the experiments were chasing:

| effect | size | verdict |
| --- | --- | --- |
| run 1, dev gain | +0.065 | about 6× the floor — **real** |
| run 1, held-out drop | −0.032 | about 3× the floor — **real** |
| run 2, held-out change | −0.0136 | at the floor |
| run 3, held-out change | −0.0005 | far below it |

### What this means

**Run 1's conclusion survives.** The memorisation it caught was three to six times larger than the noise.

**Runs 2 and 3 could not have answered their question either way.** The effects were smaller than the measurement's own variability. An earlier reading of run 2 — that the depth rule helped while the relation rule hurt — turned out to be reading signal out of noise, and run 3 was built specifically to test that claim and showed the effect was not there.

This is worth presenting as a finding, not as a failure. Knowing the resolution limit of your own instrument is a real result, and it changes what you do next: fix the instrument before running more experiments on it.

## What this establishes, and what it does not

### Established

**Structure extraction works at this scale.** Every scope, kind and parent link correct across 20 files of 800-line, 16-level-deep code, with nothing invented. Allowing for the caveats in Step 5, the 33% of scopes that are genuinely nested were still all found.

**Depth is the real limit.** Half the scopes get an exact depth, falling to one in eight past depth 14, with a consistent 5-to-1 bias toward undercounting.

**The dataset is hard for the right reason.** The model scores 0.79–0.84 on depth for shallow real code and 0.49 for deep generated code. Difficulty follows depth, not synthetic-ness.

**Free ground truth pays for itself.** It caught five bugs that code review had not — including one where a metric sat at exactly 0.000 across all 20 files, which turned out to be a pipeline bug rather than a model failure — and it caught one case of memorisation.

### Not established

**Whether prompt hints can fix depth.** Two of the three attempts produced effects smaller than the measurement's own drift. The question is still open.

**Whether this generalises to large real codebases.** The real-code set tested was short — median 24 lines. Long, messy production code has not been tried.

### What to do next

1. **Set temperature to 0.** Most of the drift is sampling. Greedy decoding should make repeat runs reproducible and collapse the noise floor.
2. **Use more files per split.** Standard error falls as the square root of the count; 20 is too few for effects of one or two points.
3. **Measure the baseline several times** and set the acceptance threshold above its spread, rather than at zero.
4. **Stop asking the model for a number.** Ask it for the list of blocks in each scope and *compute* the depth from the parent links, the way the parser does. Counting is a job for a parser; the model should only report what it can see — and on that it already scores 1.000.

That fourth point is the one most likely to move the weak metric, and it was written down before the third experiment ran rather than after.

## Questions your guide is likely to ask

**“Is this just the OPORD project again?”** The extraction spine is the same architecture with the nouns swapped — that is accurate and worth saying plainly rather than hiding. What is new: ground truth from the parser, scoring moved inside the pipeline, and a generated dataset. The OPORD project's second lane — single-command classification — has no counterpart here at all.

**“Why generate data instead of using real code?”** Because real code is flat. 45% of py150 files have no nesting; only 0.2% reach depth 14. The whole 150,000-file corpus would yield roughly 350 deep files, and 1,000 were needed. The measurement is in Step 1.

**“Four scores of 1.000 looks too good.”** Agreed, and Step 5 says which ones are flattered and by how much. The argument for trusting the rest: depth exact rate 0.489 and generator F1 0.675 come from the same code and are poor. A broken metric set would read high everywhere.

**“Did you actually train a model?”** No, and the write-up should not imply it. No weights change. What improves is the prompt's working memory. If weight training is wanted, that is a separate piece of work.

To be concrete about what the GPUs did: `gpt-oss:120b` was served across four H200s and answered several hundred requests — 20 files split into 11 to 24 sections each, 46.2 minutes for the main evaluation, plus three loop runs that re-measured both splits. All of it forward passes. There is no optimiser, no loss function, no gradient and no checkpoint anywhere in the repository, and the entire persistent output of the three loop runs is a 136-byte JSON file still at `version: 0`, because the gate rejected every candidate.

**Fine-tuning is a reasonable next project, and it is not this one.** The free ground truth would supply the labels for it — 1,000 files, every scope and block labelled exactly, which is the expensive part of any supervised run. But the measurement has to be fixed first: an effect smaller than the instrument's own ±0.011 drift is one you cannot tune against either, because you could not tell whether the tuning worked.

**“All three improvement runs failed. Is that not a negative result?”** Run 1 is a positive result about the *method*: the held-out gate caught a regression that dev-only measurement would have shipped as a 6.5-point success. Runs 2 and 3 produced the noise-floor finding. A negative result from a correctly-built experiment is worth more than a positive one from a broken experiment.

**“Why is depth so much worse than everything else?”** Because it is the only metric that requires counting rather than recognising. The error is systematic, not random: 5-to-1 undercounting, 100 of 168 misses off by exactly one, and a sharp cliff at depth 8. Step 4 has the breakdown.

**“How do you know retrieval is not leaking answers?”** Two independent guards: the index is built only from the training split, and any chunk from the file currently being extracted is dropped at query time. Verified — zero non-train chunks in the index, and the exclusion holds on a live test-split query.

## How to run it, and where things live

Code: [github.com/Arnesh03/Functional-Programming-Code---JSON-](https://github.com/Arnesh03/Functional-Programming-Code---JSON-)

```
app/        the pipeline
scripts/    generator, batch runner, improvement loop, error analysis
assets/     schema, lexicon, retrieval index
data/       the 1,000 generated programs + manifest + statistics
docs/       results.md · metrics.md · architecture-diff.md · architecture.svg
webapp/     a browser console: six tabs, five ways to view the hierarchy
```

### Things to try in front of your guide

| what | command |
| --- | --- |
| ground truth for one file, no model needed | `python3 main.py extract nested_00002 --gold` |
| the nested structure as a tree | `python3 main.py tree nested_00002` |
| one file through the model | `python3 main.py extract nested_00002 --strategy multicall` |
| 20 files with scoring | `python3 scripts/run_code_pipeline.py --count 20` |
| the browser console | `python3 webapp/server.py` |

The `--gold` option is the useful one for a demonstration: it runs every stage except the model call, so it works instantly with no GPU and no API key, and shows the pipeline end to end.

### Requirements

Python 3.10 or newer, and nothing else. The pipeline has **no hard third-party dependencies**: across all 27 source files the only non-stdlib import is `dotenv`, and it sits inside a `try/except`, so the project runs without it. Everything else is the standard library — `ast`, `json`, `sqlite3`, `urllib`, `re`, `math`, `statistics`, `hashlib`. Verified by running the whole gold path under `python3 -S -I`, which hides site-packages entirely. A language-model backend — Ollama, Groq or OpenRouter — is needed only for model runs.

### A note on the datasets

The 1,000 generated programs are in the repository. Two other corpora are deliberately **not** included: py150, because it ships only parse trees and no source text so this pipeline cannot read it, and CodeComplex, because it declares no licence. A script rebuilds the second one in two commands.

### The written record

The rest of `docs/` carries the detail behind this walkthrough: [results.md](results.md) for every run with its numbers, [metrics.md](metrics.md) for each metric and its caveats, [architecture-diff.md](architecture-diff.md) for a stage-by-stage comparison with the OPORD project, and [architecture.svg](architecture.svg) for the diagram. A 28-slide deck covers the same ground visually, and [presenting-the-deck.md](presenting-the-deck.md) explains it slide by slide.

## Appendix — the py150 corpus in detail

py150 is the public corpus used in Step 1 to show that real Python is shallow. It is worth describing properly, because the reason it is used *only* for that measurement is itself a finding.

### What it is

About 150,000 Python files collected from GitHub by the Secure, Reliable and Intelligent Systems lab at ETH Zurich. It is a standard corpus in code-modelling research, often cited for code completion.

### What is actually in the download

| file | size | contents |
| --- | --- | --- |
| `python100k_train.json` | 2.37 GB | 100,000 files, one JSON parse tree per line |
| `python50k_eval.json` | 1.15 GB | 50,000 files, same format |
| `parse_python.py` | small | the script that produced the trees |
| the tarball | 502 MB | \~3.52 GB once extracted |

### The critical property: there is no source code in it

This is the single most important fact about py150 for this project. Each file is stored as a **flat list of parse-tree nodes**, not as text. A record begins like this:

```
[{"type":"Module","children":[1,4,6,34,55]},
 {"type":"ImportFrom","children":[2],"value":"django.utils.translation"},
 {"type":"alias","children":[3],"value":"ugettext_lazy"},
 {"type":"ClassDef","children":[7,11,33],"value":"NetworkProfileTab"}, …]
```

Each node carries a type, an optional value, and the indices of its children. **The original text — the indentation, the line breaks, the comments — is gone.**

That makes py150 unusable as input to this pipeline, for two concrete reasons:

1. The sectioner splits a file by scanning **lines of text** for `def` and `class` at the left margin. There are no lines to scan.
2. The model is sent **source code** to read. There is none to send.

So py150 could never have been the test set, whatever its nesting depth had been. It can only be measured, not extracted from.

One further quirk: the trees use Python-2-era node names, so `For` may appear as `ForStatement`. The measuring script accepts both spellings, otherwise it would silently report zero.

### What the measurement found

3,001 files were scanned with the project's own measuring code. The full distribution, which the chart in Step 1 summarises into bands:

| depth | files |  | depth | files |
| --- | --- | --- | --- | --- |
| 0 | 1,362 |  | 9 | 9 |
| 1 | 798 |  | 10 | 1 |
| 2 | 414 |  | 11 | 5 |
| 3 | 198 |  | 12 | 2 |
| 4 | 92 |  | 13 | 2 |
| 5 | 56 |  | 14 | 1 |
| 6 | 31 |  | 15 | 3 |
| 7 | 14 |  | 16 | 2 |
| 8 | 8 |  | 19 | 1 |
|  |  |  | 24 | 1 |

Other figures from the same scan:

- **485 of 3,001 files (16%)** pass a filter of “nesting depth 3 or more, or contains recursion”.
- **125** of those contain a recursive function.
- **0** contain recursion inside recursion — not one file in three thousand. The generated dataset has 390.
- Mean size: **1,618 parse-tree nodes** per file, against 6,008 in the generated set.
- The deepest file found reaches depth **24**, which shows such code does exist — it is simply vanishingly rare.

### Licensing, and the redistributable version

The original py150's licence is unclear, so it is **not** included in the repository — and at 502 MB compressed with individual files above 1 GB, it would exceed GitHub's limits regardless.

Google publishes **ETH Py150 Open**, a cleaned, deduplicated and licence-filtered subset: 74,749 training, 8,302 validation and 41,457 test files, 124,508 in total. It is only about 12 kB to download, because it ships a GitHub path and a licence for each file rather than the code — you fetch the sources yourself.

### Where it is used in this project

One script, `scripts/build_nested_code_dataset.py`, which reads the parse trees directly and measures nesting. It never touches the extraction pipeline. Its output is the evidence in Step 1 and nothing else.
