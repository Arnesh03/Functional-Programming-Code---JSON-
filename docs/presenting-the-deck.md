# Nested Code → JSON: presenting the deck, slide by slide

Arnesh Singh · 30 October 2026 · [the deck](https://claude.ai/artifact/5NupPBxKAWfPUkdtVypZUH) · [the walkthrough](walkthrough.md)

One entry per slide, in deck order: what is on it, what to say while it is up, the single number that matters, and the question it invites. The deck is 28 slides — 19 in the main run, then an Appendix divider and 8 stage diagrams.

## How to use this

Each entry has the same four parts: **what is on the slide**, **what to say** while it is up, **the number that matters** if you only keep one, and **if asked** — the question that slide invites and the answer to it.

The slide numbers here are positions in the deck, 1 to 28, matching the counter in the viewer. The footer numbers printed on the slides themselves run 01 to 18 and skip the cover and the appendix, so they are one or two behind — ignore them when you are following this document.

The deck has four parts and an appendix:

| part | slides | the one thing it establishes |
| --- | --- | --- |
| 1 · The task | 1–5 | Reading structure is easy to see and hard to count — and code hands you the answer key |
| 2 · Dataset and pipeline | 6–10 | Depth had to be generated, and the file had to be split before asking |
| 3 · Results | 11–14 | Identification is solved; counting is not, and it breaks at depth 8 |
| 4 · The loop | 15–19 | Three rejections, one real catch, and a measurement that could not resolve the rest |
| Appendix | 20–28 | Each pipeline stage from the inside — for a technical review, not a talk |

Two things to say early, unprompted, because they cost you nothing when volunteered and cost you credibility if a reviewer gets there first: **the architecture is borrowed**, and **no weights were trained**. Both are on slides, both are covered below.

## Part 1 · The task, and why it is hard

### Slide 1 — Nested Code → JSON (cover)

**On the slide.** The title, a one-line framing, four chips (1,000 programs · 843,965 lines · depth 10–16 · 4×H200), and a small indented code motif.

**What to say.** “This takes a pipeline originally built to turn military operations orders into JSON, points it at Python source instead, and asks how well a large model can report the structure of deeply nested programs. The honest headline is at the end: it does the easy parts perfectly, struggles with counting depth, and the attempt to fix that ran into a measurement problem.”

Say that last clause on the cover. It sets you up as someone reporting a result rather than selling one, and everything after it lands better.

**The number that matters.** 1,000 programs, every one of them labelled exactly, at zero annotation cost.

**If asked** — “why four H200s?” Because the model is `gpt-oss:120b`, 120 billion parameters, served across four cards. It is inference, not training.

### Slide 2 — Read a program, report its structure

**On the slide.** A real Python function on the left, the JSON it should produce on the right, an arrow between them.

**What to say.** “The deliverable is not a summary of the code and not a rewrite of it. It is an index of the program's shape: every scope the file declares, every control-flow block inside it, and every relation between them — who calls whom, what recurses, what inherits.”

Point at `is_recursive: true` and `max_block_depth: 4` on the right. Those two fields are the whole story of the project: the first one the model gets right every time, the second one it gets right half the time.

**The number that matters.** None. This is the setup slide — resist quoting results here.

**If asked** — “why not just use a parser?” For Python you would, and the project does, for ground truth. The question is whether a model can do it, because for a language with no parser to hand — or for code too broken to parse — a model is the only option. Say that plainly; it is the honest motivation.

### Slide 3 — Nesting is easy to see and hard to count

**On the slide.** Eleven numbered lines of real dataset code, nested to depth 11, and a callout box titled “The `elif` trap”.

**What to say.** “Ask a person how deep that goes and they count the indents. Ask a model and it answers from impression.” Then the trap: “Python nests an `elif` one level *inside* the `if` above it, and an `except` one level inside its `try`. They look like siblings. They are not.”

This is the slide that justifies the whole project, so do not rush it. If depth were easy there would be nothing to measure.

**The number that matters.** True depth on that excerpt is 11 — printed in the bottom right corner, so you can let the audience guess first.

**If asked** — “who decides the convention?” Python's own grammar. Write `elif` and the parser creates an `If` inside the previous `If`'s `orelse` branch, so it genuinely is one level deeper. The dataset and the scoring both follow the parse tree, not the indentation.

### Slide 4 — The same pipeline, pointed at code

**On the slide.** A five-row table mapping operations-order nouns to code nouns, and three cards: ten of ten stages map, one lane has no counterpart, two stages are new.

**What to say.** Make the claim precisely, because an imprecise version is easy to attack: “The extraction spine is the same architecture with the nouns swapped. Not a new system, and not a copy. Every stage of the original's full-order lane has a counterpart here — `extract_json()` is byte-identical. The original's second lane, for single commands, has no counterpart at all. And two stages were added that neither lane had.”

**The number that matters.** Ten of ten stages mapped — and one whole lane dropped.

**If asked** — “so what is actually yours?” The two new stages, which are the next slide and the scoring, plus the dataset and every measurement. Say it in that order; it is the truthful answer and it is not a small one.

### Slide 5 — Code comes with its own answer key

**On the slide.** Two cards side by side: an operations order needs a human and the project had 6 annotated examples; a Python file is read by the parser and all 1,000 files are labelled for free. Then a green banner: every run is scored as it happens.

**What to say.** “This is the single biggest structural difference from the original project, and it is worth dwelling on. Annotation cost is normally what caps the size of an evaluation set. Here it is zero — which means the test set is the entire dataset, and scoring can be built into the pipeline instead of bolted on afterwards.”

**The number that matters.** 6 annotated examples against 1,000. That ratio is the project's pivot.

**If asked** — “using an AST for labels isn't new.” Correct, and concede it immediately. The claim is not that AST labels are novel; it is that the whole measurement architecture — total test set, inline scoring, a repeatable baseline, a self-improvement loop with a held-out gate — was designed around their being free. That was impossible in the source project with six hand-written records.

## Part 2 · The dataset and the pipeline

### Slide 6 — Nesting generated to order

**On the slide.** Four stat tiles (1,000 programs · 843,965 lines · depth 10–16 · 1000/1000 run), the list of 13 nesting templates, and a card headed “Depth is guaranteed, not intended”.

**What to say.** “Thirteen structurally different templates, because a dataset of one shape would only test one skill. The generator assembles random units until a line target is met — and then re-parses what it actually produced. Anything shallower than the floor is thrown away and regenerated.”

The card on the right is the one to emphasise. The depth figures are **measured**, not intended. That distinction is what makes the ground truth trustworthy.

**The number that matters.** 0 rejected on this build, and 1,000 of 1,000 files parse, compile and execute.

**If asked** — “isn't generated code unrealistically regular?” Partly, yes, and slide 18 concedes it. But the cross-check answers the version of the question that matters: on short real code the model scores 0.79–0.84 on depth, on the deep generated set 0.49. Difficulty tracks depth, not artificiality.

### Slide 7 — Real code is overwhelmingly shallow

**On the slide.** A horizontal bar chart of py150 nesting depth over 3,001 real GitHub files, and a banner extrapolating to the full corpus.

**What to say.** “This is the empirical justification for generating rather than scraping. Forty-five percent of real Python files have no nesting at all. Eight files in three thousand reach depth 14. At that rate the entire 150,000-file corpus holds about 400 such files — and the project needed a thousand, all deep.”

**The number that matters.** 0.27% of real files reach depth 14 or more.

**If asked** — “why not use py150 directly then?” Two answers, and the second is the stronger one. First, the depth is not there. Second, **py150 contains no source code at all** — it ships parse trees, so the indentation and line breaks are gone. The pipeline needs text to split and send, so py150 could never have been the test set whatever its depth had been. There is a full appendix on this in [the walkthrough](walkthrough.md).

### Slide 8 — Two paths in, one verdict out

**On the slide.** The architecture in three horizontal lanes: a green TRUTH lane, an amber MODEL lane of six stages, and a blue JUDGE lane. A green line runs down the left from truth to scoring.

**What to say.** Trace the green line with a finger or a cursor. “Truth is computed from the same source file, before any model is asked anything. That line is the whole reason this project can measure itself.” Then the middle lane left to right, then the bottom lane.

**The number that matters.** One — one call per definition, in the LLM box. That is the next slide.

**If asked** — “where does the validated record go?” Follow the grey return line along the bottom: back into scoring. Nothing is thrown away — a failing record is stored with its errors attached.

### Slide 9 — One file becomes one record

**On the slide.** The five top-level JSON keys as chips, then three cards listing every key of `scopes[]`, `blocks[]` and `relations[]`, with the mandatory ones in green. Below: canonical values, and two conventions.

**What to say.** “This is the contract. The model is asked for exactly this shape, the parser produces exactly this shape, and the scorer compares them key by key.” Then the two cards at the bottom, which are the interesting part: “Scoring matches on `name`, never on `scope_id` — so a model that writes `Counter.tally` where the parser writes `module.Counter.tally` is not penalised. And `depth` counts within its scope: it resets inside every nested `def`.”

**The number that matters.** 13 + 7 + 5 = 25 fields, plus `file_id` and `entrypoints[]`. For one 830-line file that is 289 separate factual claims.

**If asked** — “what if the model omits a key?” It is filled with a safe default before anything is judged: a missing `scope_id` falls back to `name`, a missing `kind` becomes `function`, ids are generated, numbers are coerced. And every `kind` is folded through a lexicon of about 60 synonyms, so `def`, `catch` and `switch` all land on the canonical word. A model is never punished for formatting — only for being wrong.

### Slide 10 — One big request, or many small ones

**On the slide.** Two cards: single call at scope F1 0.111, multicall at 0.938. A banner explaining the diagnostic.

**What to say.** “The same model, the same file. One request for the whole 830-line file returns one scope out of seventeen. Split it on top-level `def` and `class`, one request per definition, and it returns sixteen of seventeen.”

Then the banner, which is the real lesson: “The diagnosis was in the *pair* of numbers — precision 1.000 with recall 0.059. The one name it gave was real. It had not hallucinated; it had run out of room.”

**The number that matters.** 0.111 → 0.938 from splitting the input. Nothing about the model changed.

**If asked** — “how do you know it was context exhaustion and not a weak model?” The precision–recall split. High precision with near-zero recall means it stopped early; hallucination would show as low precision. This is the most practically useful slide in the deck — the same failure had already been solved once in the operations-order version, and the fix transferred.

## Part 3 · What the measurements show

### Slide 11 — 20 files, gpt-oss:120b, four H200s

**On the slide.** Eight metric tiles in two rows — four green at 1.0000, then relation F1 0.9106, generator F1 0.6752, depth exact 0.4894, and overall 0.9776 in dark.

**What to say.** “Read the green row and the amber-to-red row as two different stories. Every module, class, function and method found in every file — and then half the depths wrong.”

Then flag the next slide before anyone asks: “Four of these are exactly 1.000, and the next slide explains why, because quoting them without the caveat would be misleading.” Saying that yourself is worth more than any number on the slide.

**The number that matters.** Scope F1 is 1.0000 on **every individual file**, not an average hiding variance — 416 scopes, zero invented, zero missed.

**If asked** — “twenty files isn't much.” Agreed, and it is 416 scopes and 350 depth judgements. More importantly, slide 17 shows the splits were too small for the loop experiments, which is the honest version of this concern and you get there first.

### Slide 12 — Why four scores are exactly 1.000

**On the slide.** Four cards, one per perfect score, each explaining what inflates it. Then a green banner.

**What to say.** Go through them quickly; they are short. Scope F1: the prompt contains the roster of top-level names, so the model confirms rather than discovers. Parent accuracy: 67.3% of scopes sit at module level and the merger fills that in by default. Recursion F1: an empty prediction against an empty truth scores 1.0, and 7 of 20 files contain no recursion. Kind accuracy: the task is syntactic, so 1.000 is the expected result.

Then the banner, which is the slide's actual argument: “The reason to trust the measurement anyway is that depth exact 0.489 and generator F1 0.675 are computed the same way, and they are poor. Easy things scoring high while the hard thing scores low is what a working measurement looks like.”

**The number that matters.** 136 of 416 scopes are nested, and the roster never names those — so scope F1 is inflated but not hollow.

**If asked** — “so the headline number is meaningless?” No, but it is not the interesting one. Point at `overall` 0.9776 and say it deliberately excludes depth, which is why the loop optimises a different composite. A reviewer who spots that before you say it will not trust the rest.

### Slide 13 — There is a cliff at depth 8

**On the slide.** Ten vertical bars — exact-depth rate by true depth — green up to depth 6–7, a red divider, then red bars from depth 8 onward.

**What to say.** “Below depth 8 the model is right 59 to 100 percent of the time. At 8 and beyond it collapses to between 12 and 31 percent. Counting four levels by eye is reliable. Counting eleven is not.”

It is not a gradient, it is a wall — say that, because it is the more interesting claim and the chart supports it.

**The number that matters.** 0.12 at depth 14. One in eight.

**If asked** — “would a human do better?” Probably not much, and that is the premise the dataset was built on. This chart is the justification for the whole exercise: if depth were easy there would be nothing to measure.

### Slide 14 — It errs by omission, never invention

**On the slide.** A signed depth-error distribution on the left (−3 through +2 and up, with 182 exact), and three cards on the right: which constructs it miscounts, generators, relations.

**What to say.** “Every failure mode points the same way. 140 undercounts against 28 overcounts — a five-to-one asymmetry, mean signed error minus 0.33. That is not noise, it is a systematic bias. Generators: 23 missed, zero invented. Relations: 35 missed, 11 invented.”

Then the middle card, which is the mechanism and the best thing on the slide: “The error rate is worst exactly where the parse tree disagrees with the indentation. `while` 0.78, `finally` 0.70, `try` 0.65 — against a base rate of 0.46 to 0.48 for `for` and `if`. An `except` looks like a sibling of the `try` body and is one level deeper. All 23 missed generators had the `yield` inside a `try`.”

**The number that matters.** 5:1 undercount to overcount. The model under-reports; it does not fabricate.

**If asked** — “what does that tell you to do?” Two things. The fix should push for completeness rather than precision — and better, stop asking the model for a number at all. That is slide 19.

## Part 4 · The loop, and what it revealed

### Slide 15 — A loop that learns from its own failures

**On the slide.** Five numbered steps across the slide — measure, mine, re-measure, the gate, keep or roll back — then two cards.

**What to say.** Open with the disclaimer, not after it: “No weights change and no gradients are involved. What improves is the prompt's working memory — rules and corrected examples mined from the model's own mistakes.”

Then the gate, which is the design's whole point: “The examples are mined *from* the dev files, so improving on dev is partly memorisation. Only the untouched split can tell you whether anything generalised. A tie counts as a rejection.”

**The number that matters.** Five steps, and step 4 is the only one that decides anything.

**If asked** — “why not optimise the headline score?” Because `overall` excludes depth — a change that fixed depth perfectly would not move it by one point. The loop targets all seven metrics a prompt can actually move.

### Slide 16 — Every candidate was rejected

**On the slide.** A three-row table of the runs with dev and held-out movements and a verdict, then two cards.

**What to say.** “Three runs, three rejections, and the working memory is still at version zero. That is not a failed project — it is two findings.”

Run 1: “+6.5 points on dev against −3.2 on held-out. Measured on dev alone this would have read as a success and shipped a regression. That is the gate earning its keep, with a number on it.” Runs 2 and 3: “Real code is shallow, so only three depth errors existed to mine from twenty files. A loop needs failures to learn from.”

**The number that matters.** +0.0650 on dev, −0.0320 on held-out. One number is the trap and the other is the catch.

**If asked** — “isn't three rejections just a null result?” For runs 2 and 3, yes — and the next slide explains why they could not have been anything else. Run 1 is not null: it is a quantified instance of memorisation caught before it shipped.

### Slide 17 — The experiment could not see effects that small

**On the slide.** A brown slide — the only one in the deck — with a three-row drift table, two cards, and a red-bordered banner at the bottom.

**What to say.** This is the most important slide in the deck. Slow down. “Two runs used the same seed, so the same twenty dev and twenty held-out files. The baselines should have been identical. They were not.”

Then the consequence: “The measurement floor is about ±0.011 on the composite and up to ±0.05 on depth, purely from sampling at temperature 0.2. Run 1 at +0.065 and −0.032 is three to six times the floor — real. Runs 2 and 3, at −0.014 and −0.0005, are inside the noise.”

And then volunteer the correction in the banner: “An earlier reading of run 2 — that the depth rule helped and the relation rule hurt — was reading signal out of noise. Run 3 was built to test it and showed the effect was not there.”

**The number that matters.** ±0.011, and the +0.0490 drift on depth with identical inputs.

**If asked** — “why didn't you use greedy decoding from the start?” Fair, and it is the first item on slide 19. The point to make is that discovering this cost nothing because the ground truth is free — re-measuring a baseline is a GPU job, not an annotation job. Most projects never find their own noise floor.

### Slide 18 — What this actually established

**On the slide.** Six cards — three green ESTABLISHED, two amber NOT ESTABLISHED, one dark THE LESSON.

**What to say.** Read the labels, not the bodies; the cards are self-explanatory and reading them aloud is tedious. “Three things this shows, two it does not, and one lesson.” Then pause on the two amber ones, because volunteering limits is what makes the green ones credible.

**The number that matters.** Three established, two not. The ratio is the point.

**If asked** — “which five bugs?” The slide that listed them was cut for length; the answer is in this slide's speaker notes. Entrypoint F1 pinned at exactly 0.000 on every file, because the sectioner swallowed the `__main__` guard into the last function. An `UnboundLocalError` from the closure generator emitting its `return` before the inner `def`. 21 files rejected against CPython's limit of 20 statically nested blocks. And two console bugs — a silent re-fold on “Expand all”, and a hierarchy view blank until the first change event. None was found by code review. Each was found because a number came out wrong.

### Slide 19 — Fix the instrument, then the model

**On the slide.** Three numbered columns, a green banner, a grey card about training, and three status chips.

**What to say.** “Order matters. Running more prompt experiments on an instrument that cannot resolve the effect would burn GPU hours and produce numbers nobody can act on.” Then column three, which is the real recommendation: “Stop asking the model for a number. Ask for the block list per scope and *compute* depth from the parent links, the way the parser does.”

End on the banner: “Counting is a job for a parser. The model should only be asked to report what it can see — and on that, it already scores 1.000.” That is the closing line of the talk.

The grey card below it is the training disclaimer. Read it out rather than skipping it.

**The number that matters.** 1.000 — ending on the thing that works, after twenty minutes of what does not.

**If asked** — “why not fine-tune?” It is a reasonable next project and the free ground truth would supply the labels, which is the expensive part of any supervised run. But an effect smaller than the instrument's own ±0.011 drift is one you cannot tune against either, because you could not tell whether the tuning worked. Instrument first.

## The appendix · every stage from the inside

These nine slides are reference material, not presentation material. **Skip them in a talk.** Go through them in a technical review, where the question is usually “what does that box actually do?” — open the relevant one and answer from the diagram.

### Slide 20 — Appendix divider

A full-bleed blue slide listing the eight stages as chips. Use it as a deliberate pause: “That is the result. The rest is architecture, if you want it.” Then let them choose.

### Slide 21 — Stage 1 · gold.py, one walk and three lists

`ast.parse()` at the top, one recursive `walk_stmt` in the middle, three branches, three output lists at the bottom.

**The three conventions on this slide decide every number in the project.** Depth resets inside a nested `def`, so a closure starts counting again. An `except`, `else` or `finally` sits one level under its `try`. And an `elif` is an `If` inside `orelse`, so Python nests it and the measurement follows. Change any one and every depth figure moves.

Also worth pointing out: a call becomes a relation only if it resolves to a scope in the same file. External calls are not edges.

### Slide 22 — Stage 2 · retrieval, build once and query per section

Two lanes — BUILD offline across the top, QUERY per section at run time below, with the index as the only thing crossing between them.

The point to make is the leakage story: **two guards, not one.** The manifest keeps only `split == "train"`, and then the file being extracted is dropped from its own results. Either alone is a single point of failure, and a leak here would silently invalidate every downstream number. Verified both ways.

If asked why the diversity pass exists: the raw top-k are often near-duplicates, so `_pick_diverse` skips a repeat of the same kind and depth and takes k = 2.

### Slide 23 — Stage 3 · generation, one request per definition

The fan-out diagram: source file, sectioner, four section boxes, `merge_partials`, the record.

“Eleven to twenty-four sections per file, one request each. The merger starts from a *complete* record template, so a section that fails costs its own scopes and no top-level key goes missing.” That last clause is the design detail worth volunteering — it is why a partial failure degrades instead of breaking.

Each section prompt carries the rules, the file's roster of names, two retrieved examples and one learned example. The roster is also why scope F1 is inflated, which is slide 12 — connect the two if the question comes up.

### Slide 24 — Stage 4 · parse and normalise, before judging

Four boxes left to right — raw reply, `extract_json`, `normalize_document`, canonical record — over a panel of six lexicon foldings.

“A correct answer in the wrong words is not a wrong answer.” That is the whole slide. Without this stage the validator would reject correct extractions for spelling, and the accuracy numbers would measure prompt compliance rather than comprehension.

An unrecognised value is left alone, for the validator to flag rather than silently coerce.

### Slide 25 — Stage 5 · validate, two passes then a verdict

Shape validation, then semantic validation, then the verdict — with ERRORS and WARNINGS split below.

The line to say: **validity is not accuracy.** The run that returned 1 of 17 scopes was perfectly schema-valid, because everything it did say about itself was coherent. Validity says the record does not contradict itself; the F1 scores say whether it is true.

And **save-and-mark**: a failing record is still written, with its errors attached. A failure is evidence.

### Slide 26 — Stage 6 · score, three shapes of comparison

Prediction and gold on the left, the name index, three comparison families, and the two composites on the right.

Three quiet assumptions to state if you are being examined: name-based matching rather than ids, equal weight to every file regardless of size, and the empty-set convention that gives 7 of 20 files a free recursion F1.

The `overall` box says “no depth” for a reason — optimising it would be pointless, which is why `learning_score` exists.

### Slide 27 — Stage 7 · store and render, nine artefacts per run

The scored run fanning out into the SQLite table, the predictions folder and the two hierarchy views.

“Nine files land per run: prediction, report, tree in two formats, hierarchy in two formats, and the three gold counterparts.” That is what let the depth histogram and the construct breakdown be produced long after the GPU run had finished. Writing gold beside every prediction is what makes error analysis possible after the fact.

The console reads the same database and the same files — no second reporting path to drift out of step.

### Slide 28 — Stage 8 · the loop, a candidate must prove itself

The five steps across the top, ACCEPT and ROLL BACK below, and a red return path from rejection to the start.

This is slide 15 in detail. The one thing it adds: the candidate is written without bumping the version, so a rejection restores the champion and the loop stops. After three runs the working memory is still at v0.

End here if you are in a review: “One real catch of memorisation, and two runs whose effects fell inside the measurement's own noise.”

## If you have less time

### Ten minutes — eight slides

| # | slide | why it stays |
| --- | --- | --- |
| 1 | Cover | Frames it as a reported result, not a pitch |
| 3 | Nesting is easy to see, hard to count | Without this there is no problem to solve |
| 5 | Code comes with its own answer key | The project's pivot, in one slide |
| 7 | Real code is overwhelmingly shallow | Why the dataset is generated |
| 11 | The scores | The result |
| 12 | Why four scores are 1.000 | Credibility — never show 11 without 12 |
| 13 | The cliff at depth 8 | The finding |
| 19 | Fix the instrument, then the model | The recommendation, and the closing line |

If you are cut to five minutes, drop 7 and 13 and say the cliff in a sentence over slide 11.

### A technical review — everything, in a different order

Run the main deck as it stands, then stop at the Appendix divider and ask what they want to see. In practice the three they ask for are **slide 21** (how ground truth is computed), **slide 22** (how you know retrieval does not leak) and **slide 26** (how the scores are defined). Have those three ready and treat the rest as on-demand.

### The three questions most likely to come up

**“Did you train a model?”** No. All the GPU time was inference — a 120-billion-parameter model answering several hundred requests — plus a prompt-optimisation loop whose only persistent output is a 136-byte JSON file, still at version 0. There is no optimiser, no loss function and no checkpoint anywhere in the repository. Fine-tuning is a separate piece of work.

**“What is novel, if the architecture is borrowed?”** Choosing a task whose answer key is computable, building the measurement into the pipeline because of that, and then using it to find where a model's structural reading actually breaks — including discovering that two of your own three experiments could not resolve the effect they were testing.

**“Is this just prompt engineering?”** The extraction is. The contribution is the measurement around it: free exact ground truth for every file, scoring inside the run, an acceptance gate that caught a memorisation effect, and a quantified noise floor that says which results are real. Few prompt-engineering projects can tell you their own resolution limit.
