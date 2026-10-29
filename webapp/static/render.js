// Rendering helpers. Everything here takes data and returns HTML; nothing here fetches.

export const esc = (s) => String(s ?? "").replace(/[&<>"']/g,
  (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

const n3 = (v) => (typeof v === "number" ? v.toFixed(3) : "—");
const band = (v) => (v >= 0.9 ? "good" : v >= 0.7 ? "mid" : "poor");

/* ── documentation ─────────────────────────────────────────── */
export const PIPELINE_STAGES = [
  ["load", "read the .py file"],
  ["gold", "AST ground truth, built first", true],
  ["LLM", "single call, or one per definition"],
  ["parse", "pull the JSON out of the reply"],
  ["normalise", "lexicon spelling: def → function"],
  ["validate", "shape, then what it says about itself"],
  ["score", "compare with gold, per file", true],
  ["store", "SQLite + results/preds/"],
  ["render", "scope hierarchy"],
];

export function renderPipeline(stages) {
  return stages.map(([name, what, isNew]) => `
    <div class="stage${isNew ? " is-new" : ""}">
      <div class="stage-name">${esc(name)}</div>
      <div class="stage-what">${esc(what)}</div>
    </div>`).join("");
}

export const MODULES = [
  ["app/gold.py", "Ground truth from the AST: scopes, blocks, relations, recursion. No annotation needed."],
  ["app/llm_client.py", "Ollama / Groq / OpenRouter. The worked example in the prompt is built by gold.py, so it cannot drift."],
  ["app/multicall/", "Staged extraction: sectioner splits on top-level def/class, one request each, merge_partials joins them."],
  ["app/new_validators.py", "normalize_document (lexicon) then validate_report (errors vs warnings)."],
  ["app/evaluate.py", "Set arithmetic over names: scope F1, kind, parent, relations, depth MAE."],
  ["app/hierarchy.py", "Joins the flat record into scope → relations → blocks by depth."],
  ["app/pipeline.py", "Runs the stages in order; save-and-mark, so failures are stored not dropped."],
  ["scripts/generate_nested_code.py", "Generates the dataset: 13 nesting templates, measured and floor-checked."],
  ["scripts/run_code_pipeline.py", "Batch runner with the aggregate table."],
];

export const SCHEMA_FIELDS = [
  ["scopes[]", "scope_id, name, kind, parent_id, is_async, is_recursive, is_generator, max_block_depth, block_kinds"],
  ["blocks[]", "block_id, scope_id, kind, parent_block_id, depth, line, test — always in gold, optional from a model"],
  ["relations[]", "relation_id, relation_type (calls | self_recursive | mutually_recursive | inherits | yields_from), from_scope, to_scope"],
  ["entrypoints[]", "scope_ids reached from module level or the __main__ guard"],
];

export const COMMANDS = `# dataset (1000 files, ~850 lines each)
python3 scripts/generate_nested_code.py --count 1000 --run-check 25

# one file
python3 main.py extract nested_00002 --strategy multicall
python3 main.py hierarchy nested_00002          # ground-truth outline

# batch, with scoring against gold
python3 scripts/run_code_pipeline.py --count 20 --strategy multicall

# on the GPU box
scripts/deploy_gpu.sh inspect | push | setup | run 20 | pull

# this console
python3 webapp/server.py`;

export function table(headers, rows) {
  const head = `<thead><tr>${headers.map((h) =>
    `<th class="${h.num ? "num" : ""}">${esc(h.label ?? h)}</th>`).join("")}</tr></thead>`;
  const body = `<tbody>${rows.map((r) => `<tr${r.id ? ` data-id="${esc(r.id)}" class="clickable"` : ""}>` +
    r.cells.map((c) => `<td class="${c.num ? "num" : ""}">${c.html ?? esc(c.value ?? c)}</td>`).join("") +
    "</tr>").join("")}</tbody>`;
  return head + body;
}

/* ── stats and charts ──────────────────────────────────────── */
export function statGrid(pairs) {
  return pairs.map(([label, value]) =>
    `<div class="stat"><div class="stat-value">${esc(value)}</div>
     <div class="stat-label">${esc(label)}</div></div>`).join("");
}

export function barChart(dist, { labelPrefix = "" } = {}) {
  const entries = Object.entries(dist || {});
  if (!entries.length) return `<div class="empty">no data</div>`;
  const max = Math.max(...entries.map(([, v]) => v));
  return entries.map(([k, v]) => `
    <div class="bar-row">
      <div class="bar-label">${esc(labelPrefix + k)}</div>
      <div class="bar-track"><div class="bar-fill" style="width:${(v / max) * 100}%"></div></div>
      <div class="bar-value">${v}</div>
    </div>`).join("");
}

export function metricGrid(agg) {
  const items = [
    ["scope F1", agg.scope_f1], ["kind accuracy", agg.kind_accuracy],
    ["parent accuracy", agg.parent_accuracy], ["relation F1", agg.relation_f1],
    ["recursion F1", agg.recursive_f1], ["generator F1", agg.generator_f1],
    ["entrypoint F1", agg.entrypoint_f1], ["overall", agg.overall],
  ];
  const depth = `<div class="metric"><div class="metric-value">${(agg.depth_mae ?? 0).toFixed(2)}</div>
    <div class="metric-label">depth MAE &middot; lower is better</div></div>`;
  return items.map(([label, v]) =>
    `<div class="metric"><div class="metric-value ${band(v ?? 0)}">${n3(v)}</div>
     <div class="metric-label">${esc(label)}</div></div>`).join("") + depth;
}

/* ── validation + score for one run ────────────────────────── */
export function resultCard(res) {
  const s = res.score || {};
  const validBadge = res.is_valid
    ? `<span class="badge ok">schema valid</span>`
    : `<span class="badge bad">${res.errors.length} error${res.errors.length === 1 ? "" : "s"}</span>`;
  const warnBadge = res.warnings?.length
    ? `<span class="badge warn">${res.warnings.length} warning${res.warnings.length === 1 ? "" : "s"}</span>` : "";

  const issues = [
    ...(res.errors || []).map((e) => `<li class="err">${esc(e)}</li>`),
    ...(res.warnings || []).map((w) => `<li class="warn">${esc(w)}</li>`),
  ].join("");

  return `
    <div class="card-head">
      <h2>${esc(res.file_id)}</h2>
      <div class="row-controls">${validBadge}${warnBadge}
        <span class="chip">${esc(res.model_name || "")}</span>
        <span class="chip">${res.elapsed_s}s</span></div>
    </div>
    <div class="metricgrid">
      <div class="metric"><div class="metric-value ${band(s.overall ?? 0)}">${n3(s.overall)}</div>
        <div class="metric-label">overall</div></div>
      <div class="metric"><div class="metric-value ${band(s.scopes?.f1 ?? 0)}">${n3(s.scopes?.f1)}</div>
        <div class="metric-label">scope F1 &middot; ${s.scopes?.tp}/${s.scopes?.n_gold} found</div></div>
      <div class="metric"><div class="metric-value ${band(s.kind_accuracy ?? 0)}">${n3(s.kind_accuracy)}</div>
        <div class="metric-label">kind accuracy</div></div>
      <div class="metric"><div class="metric-value ${band(s.parent_accuracy ?? 0)}">${n3(s.parent_accuracy)}</div>
        <div class="metric-label">parent accuracy</div></div>
      <div class="metric"><div class="metric-value ${band(s.relations?.f1 ?? 0)}">${n3(s.relations?.f1)}</div>
        <div class="metric-label">relation F1</div></div>
      <div class="metric"><div class="metric-value">${(s.max_block_depth?.mae ?? 0).toFixed(2)}</div>
        <div class="metric-label">depth MAE</div></div>
    </div>
    ${issues ? `<h3>Validation</h3><ul class="issues">${issues}</ul>` : ""}
    <h3>Hierarchy</h3>
    <div class="tree">${scopeTree(res.hierarchy)}</div>`;
}

/* ── the scope hierarchy ───────────────────────────────────── */
export function scopeTree(view, { maxBlocks = 40 } = {}) {
  const scopes = view?.scopes || [];
  if (!scopes.length) return `<div class="empty">no scopes</div>`;

  return scopes.map((s) => {
    const flags = [
      s.is_recursive ? `<span class="flag rec">recursive</span>` : "",
      s.is_generator ? `<span class="flag gen">generator</span>` : "",
      s.is_async ? `<span class="flag">async</span>` : "",
    ].join("");

    const rels = (s.structure || []).filter((r) => r.kind !== "standing");
    const relLine = rels.length ? `<div class="scope-rels">${rels.slice(0, 10).map((r) =>
      `${esc(r.relation_type)} ${r.role === "from" ? "→" : "←"} ${esc(r.counterpart_name || "?")}`
    ).join(" &middot; ")}${rels.length > 10 ? ` &middot; +${rels.length - 10}` : ""}</div>` : "";

    const flat = Object.values(s.blocks || {}).flat();
    const known = new Set(flat.map((b) => b.block_id));
    const kids = new Map();
    for (const b of flat) {
      const key = known.has(b.parent_block_id) ? b.parent_block_id : "";
      if (!kids.has(key)) kids.set(key, []);
      kids.get(key).push(b);
    }
    for (const list of kids.values()) list.sort((a, b) => a.line - b.line);

    let shown = 0;
    const lines = [];
    const walk = (key) => {
      for (const b of kids.get(key) || []) {
        if (shown >= maxBlocks) return;
        const indent = "  ".repeat(Math.max(0, b.depth - 1));
        lines.push(`<div class="block-line">${indent}<span class="block-kind">${esc(b.kind)}</span>` +
          (b.test ? ` <span class="block-test">${esc(b.test)}</span>` : "") +
          ` <span class="block-line-no">:${b.line}</span></div>`);
        shown++;
        walk(b.block_id);
      }
    };
    walk("");
    const more = flat.length > shown ? `<div class="block-line block-line-no">… ${flat.length - shown} more</div>` : "";

    return `<div class="scope-node" style="margin-left:${(s.scope_nesting || 0) * 14}px">
      <div class="scope-head">
        <span class="scope-sig">${esc(s.signature)}</span>
        <span class="scope-kind">${esc(s.kind)}</span>
        <span class="scope-meta">depth ${s.max_block_depth} &middot; L${s.start_line}-${s.end_line}</span>
        ${flags}
      </div>
      ${relLine}${lines.join("")}${more}
    </div>`;
  }).join("");
}

export function jsonBlock(obj) {
  return `<pre class="code">${esc(JSON.stringify(obj, null, 2))}</pre>`;
}

/* ── visual nested tree ────────────────────────────────────── */
const BLOCK_CLASS = {
  for: "vloop", async_for: "vloop", while: "vloop",
  if: "vbranch", else: "vbranch",
  try: "verror", except: "verror", finally: "verror",
  with: "vctx", async_with: "vctx",
  match: "vmatch", case: "vmatch",
};

const depthClass = (d) => (d >= 9 ? "hot" : d >= 5 ? "warm" : "");

function vnode(node, depth) {
  const kids = node.children || [];
  const toggle = `<span class="vtoggle${kids.length ? "" : " leaf"}">${kids.length ? "−" : ""}</span>`;

  let body;
  if (node.node_type === "scope") {
    const flags = (node.flags || []).map((f) =>
      `<span class="flag ${f === "recursive" ? "rec" : f === "generator" ? "gen" : ""}">${esc(f)}</span>`).join("");
    const counts = node.counts || {};
    const sub = (counts.scopes || counts.blocks)
      ? `<span class="vcount">${counts.scopes ? `${counts.scopes} scopes · ` : ""}${counts.blocks} blocks</span>` : "";
    body = `<span class="vkind ${esc(node.kind)}">${esc(node.kind)}</span>` +
      `<span class="vlabel">${esc(node.label)}</span>` +
      `<span class="vmeta">L${node.start_line}–${node.end_line}</span>` +
      `<span class="vdepth ${depthClass(node.max_block_depth)}">depth ${node.max_block_depth}</span>` +
      flags + sub;
  } else {
    body = `<span class="${BLOCK_CLASS[node.kind] || ""}">${esc(node.kind)}</span>` +
      (node.test ? ` <span class="vtest">${esc(node.test)}</span>` : "") +
      ` <span class="vline">:${node.line}</span>`;
  }

  const inner = kids.length
    ? `<ul>${kids.map((k) => vnode(k, depth + 1)).join("")}</ul>` : "";
  // Deep block chains start collapsed, or an 11-level pyramid buries everything after it.
  const collapsed = node.node_type === "block" && depth > 6 && kids.length ? " class=\"collapsed\"" : "";
  return `<li${collapsed}><span class="vnode ${node.node_type === "scope" ? "is-scope" : ""}">${toggle}${body}</span>${inner}</li>`;
}

export function visualTree(tree) {
  const root = tree?.root;
  if (!root) return `<div class="empty">no tree</div>`;
  const t = tree.totals || {};
  return `
    <div class="vtoolbar">
      <button class="btn-ghost" data-vtree="expand" type="button">Expand all</button>
      <button class="btn-ghost" data-vtree="collapse" type="button">Collapse blocks</button>
      <div class="vtotals">
        <span class="chip">${t.scopes ?? "?"} scopes</span>
        <span class="chip">${t.blocks ?? "?"} blocks</span>
        <span class="chip">${t.relations ?? 0} relations</span>
        <span class="chip">max depth ${t.max_depth ?? "?"}</span>
      </div>
    </div>
    <div class="vlegend">
      <span><i class="vdot" style="background:#a57aff"></i>module / with</span>
      <span><i class="vdot" style="background:#f0913c"></i>class</span>
      <span><i class="vdot" style="background:#4f9cf9"></i>function / if</span>
      <span><i class="vdot" style="background:#2dc8be"></i>async</span>
      <span><i class="vdot" style="background:#3fb950"></i>method</span>
      <span><i class="vdot" style="background:#f0b429"></i>loops</span>
      <span><i class="vdot" style="background:#f85149"></i>try / except</span>
      <span><i class="vdot" style="background:#ee6ebb"></i>match</span>
    </div>
    <div class="vtree"><ul>${vnode(root, 0)}</ul></div>`;
}

export function bindTree(container) {
  container.querySelectorAll(".vtoggle").forEach((t) => t.addEventListener("click", (e) => {
    e.stopPropagation();
    const li = t.closest("li");
    li.classList.toggle("collapsed");
    t.textContent = li.classList.contains("collapsed") ? "+" : "−";
  }));
  container.querySelectorAll("[data-vtree]").forEach((btn) => btn.addEventListener("click", () => {
    const collapse = btn.dataset.vtree === "collapse";
    container.querySelectorAll(".vtree li").forEach((li) => {
      const isBlock = !li.querySelector(":scope > .vnode.is-scope");
      const has = li.querySelector(":scope > ul");
      if (!has) return;
      li.classList.toggle("collapsed", collapse && isBlock);
      const tog = li.querySelector(":scope > .vnode > .vtoggle");
      if (tog) tog.textContent = li.classList.contains("collapsed") ? "+" : "−";
    });
  }));
}

/* ── node-link tree diagram ────────────────────────────────── */
// A tidy left-to-right tree: depth sets x, leaf order sets y, and every internal node is
// centred on its children. Deep block chains are folded by default — an 11-level loop pyramid
// drawn in full is 250 nodes tall and legible to nobody.

const NODE_FILL = {
  module: "#a57aff", class: "#f0913c", function: "#4f9cf9",
  async_function: "#2dc8be", method: "#3fb950", async_method: "#2dc8be",
  for: "#f0b429", async_for: "#f0b429", while: "#f0b429",
  if: "#4f9cf9", else: "#4f9cf9",
  try: "#f85149", except: "#f85149", finally: "#f85149",
  with: "#a57aff", async_with: "#a57aff",
  match: "#ee6ebb", case: "#ee6ebb",
};

const X_GAP = 215, Y_GAP = 26, NODE_H = 20;

function diagramLabel(node) {
  if (node.node_type === "scope") return node.label;
  return node.kind + (node.test ? ` ${node.test}` : "");
}

export function layoutTree(root, collapsed) {
  const nodes = [], edges = [];
  let cursor = 0;

  const walk = (node, depth, parent, path) => {
    const id = path;
    const kids = node.children || [];
    const isCollapsed = collapsed.has(id);
    const rec = {
      id, depth, node, label: diagramLabel(node),
      type: node.node_type, kind: node.kind,
      hidden: kids.length ? isCollapsed : false,
      nKids: kids.length,
      descendants: (node.counts?.scopes || 0) + (node.counts?.blocks || 0),
    };
    nodes.push(rec);
    if (parent) edges.push({ from: parent, to: rec });

    if (kids.length && !isCollapsed) {
      const placed = kids.map((k, i) => walk(k, depth + 1, rec, `${id}/${i}`));
      rec.y = (placed[0].y + placed[placed.length - 1].y) / 2;
    } else {
      rec.y = cursor;
      cursor += Y_GAP;
    }
    rec.x = depth * X_GAP;
    return rec;
  };

  walk(root, 0, null, "r");
  return { nodes, edges, height: Math.max(cursor, Y_GAP), depth: Math.max(...nodes.map((n) => n.depth)) };
}

export function treeDiagram(tree, collapsed) {
  const root = tree?.root;
  if (!root) return `<div class="empty">no tree</div>`;
  const { nodes, edges, height, depth } = layoutTree(root, collapsed);

  const width = (depth + 1) * X_GAP + 60;
  const h = height + 50;

  const edgePaths = edges.map((e) => {
    const x1 = e.from.x + nodeWidth(e.from), y1 = e.from.y + NODE_H / 2;
    const x2 = e.to.x, y2 = e.to.y + NODE_H / 2;
    const mid = x1 + (x2 - x1) / 2;
    return `<path class="dg-edge" d="M${x1},${y1} C${mid},${y1} ${mid},${y2} ${x2},${y2}"/>`;
  }).join("");

  const nodeShapes = nodes.map((n) => {
    const w = nodeWidth(n);
    const fill = NODE_FILL[n.kind] || "#6b7a8c";
    const isScope = n.type === "scope";
    const badge = n.hidden && n.descendants
      ? `<text class="dg-badge" x="${n.x + w + 7}" y="${n.y + NODE_H / 2 + 4}">+${n.descendants}</text>` : "";
    const marker = n.nKids
      ? `<circle class="dg-toggle" data-node="${esc(n.id)}" cx="${n.x + w + (n.hidden ? 0 : 0)}" cy="${n.y + NODE_H / 2}" r="4.5"
           fill="${n.hidden ? fill : "var(--bg)"}" stroke="${fill}" stroke-width="1.4"/>` : "";
    return `<g class="dg-node" data-node="${esc(n.id)}">
      <rect x="${n.x}" y="${n.y}" width="${w}" height="${NODE_H}" rx="5"
            fill="${fill}1f" stroke="${fill}" stroke-width="${isScope ? 1.3 : 0.8}"/>
      <text class="dg-text${isScope ? " is-scope" : ""}" x="${n.x + 8}" y="${n.y + NODE_H / 2 + 4}"
            fill="${isScope ? fill : "currentColor"}">${esc(truncate(n.label, 26))}</text>
      ${marker}${badge}
    </g>`;
  }).join("");

  return `
    <div class="dg-toolbar">
      <button class="btn-ghost" data-dg="scopes" type="button">Scopes only</button>
      <button class="btn-ghost" data-dg="all" type="button">Everything</button>
      <button class="btn-ghost" data-dg="zoom-out" type="button">−</button>
      <button class="btn-ghost" data-dg="zoom-in" type="button">+</button>
      <span class="vmeta">click a node's dot to fold · drag to pan</span>
      <div class="vtotals">
        <span class="chip">${nodes.length} drawn</span>
        <span class="chip">depth ${depth}</span>
      </div>
    </div>
    <div class="dg-wrap">
      <svg class="dg-svg" width="${width}" height="${h}" viewBox="0 0 ${width} ${h}">
        <g class="dg-pan">${edgePaths}${nodeShapes}</g>
      </svg>
    </div>`;
}

const truncate = (s, n) => (s.length > n ? s.slice(0, n - 1) + "…" : s);
const nodeWidth = (n) => Math.min(190, Math.max(54, truncate(n.label, 26).length * 7 + 18));

export function collapseDefaults(root, mode = "scopes") {
  // "scopes" folds every block; "all" shows the lot.
  const collapsed = new Set();
  const walk = (node, path) => {
    const kids = node.children || [];
    if (mode === "scopes" && node.node_type === "block" && kids.length) collapsed.add(path);
    kids.forEach((k, i) => walk(k, `${path}/${i}`));
  };
  walk(root, "r");
  if (mode === "scopes") {
    // Fold a scope's blocks at the top too, so each scope shows as one box.
    const fold = (node, path) => {
      (node.children || []).forEach((k, i) => {
        const p = `${path}/${i}`;
        if (k.node_type === "block") collapsed.add(p);
        else fold(k, p);
      });
    };
    fold(root, "r");
  }
  return collapsed;
}

export function bindDiagram(container, tree, state, repaint) {
  container.querySelectorAll(".dg-toggle").forEach((el) => el.addEventListener("click", (e) => {
    e.stopPropagation();
    const id = el.dataset.node;
    state.collapsed.has(id) ? state.collapsed.delete(id) : state.collapsed.add(id);
    repaint();
  }));
  container.querySelectorAll("[data-dg]").forEach((btn) => btn.addEventListener("click", () => {
    const what = btn.dataset.dg;
    if (what === "scopes") state.collapsed = collapseDefaults(tree.root, "scopes");
    else if (what === "all") state.collapsed = new Set();
    else state.zoom = Math.min(2, Math.max(0.25, state.zoom + (what === "zoom-in" ? 0.15 : -0.15)));
    repaint();
  }));

  const svg = container.querySelector(".dg-svg");
  if (!svg) return;
  svg.style.transformOrigin = "0 0";
  svg.style.transform = `scale(${state.zoom})`;

  // drag to pan the scroll container
  const wrap = container.querySelector(".dg-wrap");
  let down = false, sx = 0, sy = 0, sl = 0, st = 0;
  wrap.addEventListener("mousedown", (e) => {
    if (e.target.closest(".dg-toggle")) return;
    down = true; sx = e.clientX; sy = e.clientY; sl = wrap.scrollLeft; st = wrap.scrollTop;
    wrap.style.cursor = "grabbing";
  });
  window.addEventListener("mouseup", () => { down = false; wrap.style.cursor = ""; });
  wrap.addEventListener("mousemove", (e) => {
    if (!down) return;
    wrap.scrollLeft = sl - (e.clientX - sx);
    wrap.scrollTop = st - (e.clientY - sy);
  });
}

/* ── OPORD comparison ──────────────────────────────────────── */
// Kept as data so the page and docs/architecture-diff.md say the same thing.

export const STAGE_DIFF = [
  ["Load", "_load_opord_text — .docx / .txt", "_load_source — .py", "same"],
  ["Context", "RAG: Chroma over 3 doctrine docs, k=6", "RAG: TF-IDF over solved train sections, k=2", "same"],
  ["Ground truth", "hand-written gold JSON per example", "gold.py reads the AST", "new"],
  ["Generate", "generate_opord_json", "generate_code_json", "same"],
  ["Staged path", "multicall — 4 fixed passes", "multicall — one pass per definition", "same"],
  ["Parse", "extract_json", "extract_json — unchanged file", "same"],
  ["Normalise", "normalize_document", "normalize_document", "same"],
  ["Validate", "validate_report", "validate_report", "same"],
  ["Score", "separate script, run afterwards", "inline, every run", "changed"],
  ["Persist", "SQLite opord_runs + results/preds/", "SQLite code_runs + same convention", "same"],
  ["Hierarchy", "to_unit_hierarchy", "to_scope_hierarchy + to_nested_tree", "new"],
  ["Console", "webapp, 4 tabs", "webapp, 6 tabs", "same"],
  ["Self-improvement", "auto_improve.py + learned_hints.py", "auto_improve.py + learned_hints.py", "same"],
];

export const MODULE_DIFF = {
  carried: ["config.py", "llm_client.py", "retriever.py", "rag_store.py", "new_validators.py", "pipeline.py", "hierarchy.py",
            "logger.py", "utils.py", "multicall/sectioner.py", "multicall/segment_prompts.py",
            "multicall/merge_partials.py"],
  dropped: [
    ["single_command_pipeline + 3 scripts", "a second task with no code analogue"],
    ["context_card · execution_contract · support_contract", "military concepts with nothing to map onto"],
    ["battalion_opord_eval · run_batch_eval · compare_strategies", "replaced by inline evaluate.py"],
    ["oporder_worker.py", "Celery worker, not needed"],
  ],
  added: [
    ["app/gold.py", "AST ground truth — scopes, blocks, relations, recursion, depth"],
    ["app/evaluate.py", "scope F1, kind, parent, relation F1, depth MAE — inline"],
    ["scripts/generate_nested_code.py", "the dataset: 13 templates, measured and floor-checked"],
    ["scripts/deploy_gpu.sh", "inspect / push / setup / run / pull on the GPU box"],
    ["app/learned_hints.py", "working memory — rules + corrected examples, read by both prompt builders"],
    ["scripts/auto_improve.py", "mines failures; keeps a version only if it beats the held-out split"],
    ["app/rag_store.py + retriever.py", "retrieval over solved train sections — train split only, no leakage"],
  ],
};

export const SCALE_DIFF = [
  ["Schema top-level keys", "19", "5", "an order says many kinds of thing; code has few types that nest arbitrarily"],
  ["Lexicon groups", "13", "6", "echelons, task_verbs, time_kinds… → scope_kinds, block_kinds, relation_types"],
  ["Multicall passes", "4, fixed", "11–24, file-driven", "split on headings → split on top-level def/class"],
  ["Gold coverage", "6 examples", "all 1000 samples", "hand-written → derived from the parser"],
  ["Retrieval corpus", "3 doctrine documents", "3,305 solved sections", "doctrine → worked examples with known answers"],
  ["Stages still missing", "—", "none", "retrieval, scoring and self-improvement are all in"],
];

export const HIERARCHY_MAP = [
  ["unit", "scope (module / class / function / method)"],
  ["phase — the ordered axis", "nesting depth — the ordered axis"],
  ["ALL_PHASES bucket", "ANY_DEPTH bucket"],
  ["tasks bucketed by phase", "blocks bucketed by depth"],
  ["units parents-first, by chain of command", "scopes parents-first, by lexical nesting"],
  ["unassigned: task names an undeclared unit", "unassigned: block names an undeclared scope"],
];

export const UNCHANGED = [
  ["Save-and-mark", "validation never blocks a write — a failed extraction is evidence"],
  ["Normalise before judging", "occupies → occupy became def → function"],
  ["Errors vs warnings", "errors are facts the record gets wrong about itself; warnings are survivable"],
  ["Dangling references kept", "so the reading view agrees with the validator that reports them"],
];

export function diffTable(rows) {
  const verdictBadge = (v) => `<span class="verdict ${v}">${esc(v)}</span>`;
  return table(["Stage", "OPORD → JSON", "Nested Code → JSON", "Verdict"],
    rows.map(([stage, a, b, v]) => ({
      cells: [
        { html: `<b>${esc(stage)}</b>` },
        { html: `<span class="muted">${esc(a)}</span>` },
        { value: b },
        { html: verdictBadge(v) },
      ],
    })));
}

/* ── recorded results ──────────────────────────────────────── */
export const HEADLINE = [
  ["scope F1", "1.0000", "good"], ["kind accuracy", "1.0000", "good"],
  ["parent accuracy", "1.0000", "good"], ["recursion F1", "1.0000", "good"],
  ["relation F1", "0.9106", "good"], ["generator F1", "0.6752", "poor"],
  ["depth exact", "0.4894", "poor"], ["overall", "0.9776", "good"],
];

export const RUN_HISTORY = [
  ["Dataset build", "generator", "1000 files · 843,965 lines", "0 rejected, 0 duplicates, 1000/1000 execute", "—"],
  ["Plumbing check", "gold · no model", "5 + 3 + 3 files", "every metric 1.000", "1.0000"],
  ["One file, single call", "qwen3:4b · laptop", "nested_00002", "1 of 17 scopes returned", "0.5278"],
  ["One file, multicall", "qwen3:4b · laptop", "nested_00002", "15 of 17 scopes · 1,172 s", "0.8302"],
  ["One file, multicall", "gpt-oss:120b · H200", "nested_00002", "all 17 scopes · 110 s", "0.9750"],
  ["Main evaluation", "gpt-oss:120b · H200", "20 files · 46.2 min", "scope F1 1.000 on every file · 20/20 valid", "0.9776"],
  ["After sectioner fix", "gpt-oss:120b · H200", "nested_00002", "entrypoint F1 0.000 → 1.000", "0.9881"],
  ["Training baseline", "gpt-oss:120b · H200", "6 dev · 6 held out", "learning_score: dev 0.7090 · held-out 0.7896", "0.7896"],
  ["Training round 1", "gpt-oss:120b · H200", "84.1 min · 24 extractions", "dev +0.065 but held-out −0.032 → REJECTED, rolled back to v0", "0.7576"],
];

export const BUGS_FOUND = [
  ["entrypoint F1 = 0.000 on all 20 files", "the sectioner swallowed the __main__ guard into the last function's section", "0.000 → 1.000"],
  ["UnboundLocalError at runtime", "closure generator emitted `return level1` before `def level1`", "all 1000 files execute"],
  ["too many statically nested blocks", "CPython allows 20 per code object; try_pyramid spent two per level", "21 rejections → 0"],
  ["\"Expand all\" silently re-folded", "an empty collapsed-set read as \"not initialised\"", "43 → 250 nodes"],
];

export function headlineGrid(items) {
  return items.map(([label, value, band]) =>
    `<div class="metric"><div class="metric-value ${band}">${esc(value)}</div>
     <div class="metric-label">${esc(label)}</div></div>`).join("");
}

/* ── metric explanations ───────────────────────────────────── */
export const METRIC_DOCS = [
  ["scope F1", "1.0000",
   "Set F1 over bare scope names. Precision &lt; 1 = invented scopes; recall &lt; 1 = missed ones.",
   "416 scopes, zero invented, zero missed. But the roster of top-level names is in the prompt, so the real work was the 136 nested scopes (32.7%).", "caveat"],
  ["kind accuracy", "1.0000",
   "Share of scopes present in <em>both</em> records that got the same kind. Independent of scope F1.",
   "Expected. The distinction is syntactic: def at column zero = function, def inside class = method.", "easy"],
  ["parent accuracy", "1.0000",
   "Same shape, comparing the <em>name</em> of the enclosing scope.",
   "67.3% of scopes are module-level and the merger defaults parent to \"module\", so two-thirds is a default, not a decision.", "caveat"],
  ["recursion F1", "1.0000",
   "Set F1 over scopes flagged is_recursive.",
   "22 recursive scopes in 416, and 7 of 20 files have none — an empty-vs-empty comparison scores 1.0, so 35% are free wins.", "caveat"],
  ["generator F1", "0.6752",
   "Set F1 over scopes flagged is_generator.",
   "Generators appear in every file, so there are no free 1.0s — and the score drops. yield buried in a nested try or loop gets missed.", "real"],
  ["relation F1", "0.9106",
   "Set F1 over (relation_type, from_name, to_name) triples. All three must match.",
   "The hardest thing it mostly gets right: notice a call AND decide if it is a plain call, self-recursion or mutual recursion.", "real"],
  ["entrypoint F1", "1.0000",
   "Set F1 over names reached from module level or the __main__ guard.",
   "Was 0.0000 on every file — not model failure, the sectioner swallowed the __main__ guard. A metric pinned at exactly 0 is usually a pipeline bug.", "fixed"],
  ["depth MAE", "0.8437",
   "Mean absolute error in nesting levels, over scopes where either depth is non-zero.",
   "The typical miss is under one level — systematically slightly off, which is what a prompt correction can fix. qwen3:4b was at 3.00.", "real"],
  ["depth exact", "0.4894",
   "Share of scopes whose depth was exactly right.",
   "About half. This is the honest weak point and the reason the self-improvement loop exists.", "real"],
  ["overall", "0.9776",
   "mean(scope F1, relation F1, kind, parent). Frozen so all runs stay comparable.",
   "Excludes depth, generators and entrypoints — so it is flattered by the three metrics sitting at 1.000. Quote it for continuity, quote sub-metrics for quality.", "caveat"],
  ["learning_score", "—",
   "mean of all seven movable metrics, including depth exact.",
   "What the training loop optimises. Optimising overall would be pointless: fixing depth perfectly would not move it one point.", "easy"],
  ["schema-valid", "20/20",
   "Not accuracy. A record is valid when it makes no false claims about itself.",
   "A record can be 100% valid and completely wrong — the run that returned 1 of 17 scopes was valid. Validity = coherent; F1 = true.", "easy"],
];

const BAND_LABEL = { caveat: "read the caveat", real: "honest signal", easy: "expected", fixed: "was a bug" };

export function metricDocs(rows) {
  return rows.map(([name, score, how, reading, band]) => `
    <div class="mdoc">
      <div class="mdoc-head">
        <span class="mdoc-name">${esc(name)}</span>
        <span class="mdoc-score">${esc(score)}</span>
        <span class="verdict ${band === "caveat" ? "changed" : band === "real" ? "new" : band === "fixed" ? "dropped" : "same"}">${esc(BAND_LABEL[band])}</span>
      </div>
      <div class="mdoc-how">${how}</div>
      <div class="mdoc-read">${esc(reading)}</div>
    </div>`).join("");
}


/* ── error analysis headlines ──────────────────────────────── */
export const ERROR_FINDINGS = [
  ["Depth errors are undercounts, 5:1",
   "140 undercounts vs 28 overcounts · mean signed −0.329 · 100 of 168 misses are off by exactly one",
   "A directional bias is correctable by instruction in a way random noise is not."],
  ["There is a cliff at depth 8",
   "depth 1–7: exact 0.59–1.00 · depth 8+: exact 0.12–0.31",
   "Counting four levels by eye is reliable; counting eleven is not — which is the premise of the dataset."],
  ["try / except / finally / while are where it breaks",
   "while 0.78 error rate · finally 0.70 · try 0.65 · except 0.64 — vs for 0.48 and if 0.46",
   "An except is a sibling in the source but one level deeper in the AST."],
  ["Generator misses are pure recall",
   "23 missed · 0 invented — mostly tracked / async_tracked / arange",
   "The yield sits inside a try block. One structural pattern explains most of the 0.6752."],
  ["The loop rejected its own candidate — and that is the result",
   "dev 0.598 → 0.665 depth exact (+0.067) · held-out 0.702 → 0.652 (−0.050) · 4 of 6 held-out files got worse",
   "Textbook memorisation, caught. Measured on dev alone this would have read as \"+6.5 points, it works\" — and shipped a regression."],
  ["The training loop independently confirmed all of this",
   "different 6 files · depth mean −0.84 · 42 missed relations vs 0 invented · 19 generator errors",
   "Two independent samples, two independently written pieces of code, same conclusion — the error is a property of the model, not of one sample."],
  ["Relations too: 3:1 missed to invented",
   "calls: 35 missed, 11 invented · yields_from: 8 missed, 0 invented",
   "This model errs by omission, not invention — push for completeness, not precision."],
];

export function findings(rows) {
  return rows.map(([title, nums, why]) => `
    <div class="mdoc">
      <div class="mdoc-head"><span class="mdoc-name">${esc(title)}</span></div>
      <div class="mdoc-how"><code>${esc(nums)}</code></div>
      <div class="mdoc-read">${esc(why)}</div>
    </div>`).join("");
}
