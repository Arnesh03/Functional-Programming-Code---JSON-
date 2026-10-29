// Wiring: fetches, tab switching, and putting rendered HTML where it belongs.
import {
  BUGS_FOUND, COMMANDS, ERROR_FINDINGS, HEADLINE, METRIC_DOCS, findings, metricDocs, HIERARCHY_MAP, MODULES, RUN_HISTORY, headlineGrid, MODULE_DIFF, PIPELINE_STAGES, SCALE_DIFF, SCHEMA_FIELDS,
  STAGE_DIFF, UNCHANGED, barChart, bindDiagram, bindTree, collapseDefaults, diffTable, esc,
  jsonBlock, metricGrid, renderPipeline, resultCard, scopeTree, statGrid, table, treeDiagram,
  visualTree,
} from "/render.js";

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));

const state = { samples: [], stats: {}, metrics: [], current: null };

async function api(path, options) {
  const res = await fetch(path, options);
  const data = await res.json().catch(() => ({ error: `${res.status} ${res.statusText}` }));
  if (!res.ok || data.error) throw new Error(data.error || `${res.status}`);
  return data;
}

function toast(msg, bad = false) {
  const el = $("#toast");
  el.textContent = msg;
  el.className = `show${bad ? " bad" : ""}`;
  setTimeout(() => (el.className = ""), 3200);
}

/* ── tabs ──────────────────────────────────────────────────── */
$$(".tab").forEach((tab) => tab.addEventListener("click", () => {
  $$(".tab").forEach((t) => { t.classList.remove("is-active"); t.setAttribute("aria-selected", "false"); });
  tab.classList.add("is-active");
  tab.setAttribute("aria-selected", "true");
  $$(".panel").forEach((p) => (p.hidden = true));
  $(`#panel-${tab.dataset.tab}`).hidden = false;
  if (tab.dataset.tab === "eval") loadMetrics();
  if (tab.dataset.tab === "history") loadHistory();
  // Opening the tab should show something; waiting for a `change` event leaves it blank.
  if (tab.dataset.tab === "hierarchy" && !hierarchyData) loadHierarchy();
}));

/* ── overview ──────────────────────────────────────────────── */
function renderDocs() {
  $("#pipeline-diagram").innerHTML = renderPipeline(PIPELINE_STAGES);
  $("#modules-table").innerHTML = table(["Module", "Does"],
    MODULES.map(([m, d]) => ({ cells: [{ html: `<code>${esc(m)}</code>` }, d] })));
  $("#schema-table").innerHTML = table(["Key", "Fields"],
    SCHEMA_FIELDS.map(([k, v]) => ({ cells: [{ html: `<code>${esc(k)}</code>` }, v] })));
  $("#headline").innerHTML = headlineGrid(HEADLINE);
  $("#run-history").innerHTML = table(
    ["Run", "Where", "Scale", "What happened", { label: "overall", num: true }],
    RUN_HISTORY.map(([run, where, scale, what, score]) => ({
      cells: [{ html: `<b>${esc(run)}</b>` }, { html: `<code>${esc(where)}</code>` },
              { value: scale }, { html: `<span class="muted">${esc(what)}</span>` },
              { html: `<b>${esc(score)}</b>`, num: true }],
    })));
  $("#metric-docs").innerHTML = metricDocs(METRIC_DOCS);
  $("#error-findings").innerHTML = findings(ERROR_FINDINGS);
  $("#bugs-found").innerHTML = table(["Symptom", "Cause", "Effect of the fix"],
    BUGS_FOUND.map(([s1, c, e]) => ({
      cells: [{ value: s1 }, { html: `<span class="muted">${esc(c)}</span>` },
              { html: `<b>${esc(e)}</b>` }] })));
  $("#stage-diff").innerHTML = diffTable(STAGE_DIFF);
  $("#scale-diff").innerHTML = table(
    ["", "OPORD", "Code", "Why"],
    SCALE_DIFF.map(([what, a, b, why]) => ({
      cells: [{ html: `<b>${esc(what)}</b>` }, { html: `<span class="muted">${esc(a)}</span>` },
              { value: b }, { html: `<span class="muted">${esc(why)}</span>` }],
    })));
  $("#hierarchy-map").innerHTML = table(["OPORD", "Code"],
    HIERARCHY_MAP.map(([a, b]) => ({
      cells: [{ html: `<span class="muted">${esc(a)}</span>` }, { value: b }] })));
  $("#unchanged").innerHTML = table(["Commitment", "What it means"],
    UNCHANGED.map(([a, b]) => ({ cells: [{ html: `<b>${esc(a)}</b>` }, b] })));
  $("#module-diff").innerHTML = `
    <div class="col-card">
      <h4><span class="verdict same">carried over</span> ${MODULE_DIFF.carried.length} modules</h4>
      <ul>${MODULE_DIFF.carried.map((m) => `<li><code>${esc(m)}</code></li>`).join("")}</ul>
    </div>
    <div class="col-card">
      <h4><span class="verdict dropped">dropped</span> ${MODULE_DIFF.dropped.length} groups</h4>
      <ul>${MODULE_DIFF.dropped.map(([m, why]) =>
        `<li><code>${esc(m)}</code><br>${esc(why)}</li>`).join("")}</ul>
    </div>
    <div class="col-card">
      <h4><span class="verdict new">new</span> ${MODULE_DIFF.added.length} modules</h4>
      <ul>${MODULE_DIFF.added.map(([m, why]) =>
        `<li><code>${esc(m)}</code><br>${esc(why)}</li>`).join("")}</ul>
    </div>`;
  $("#commands").textContent = COMMANDS;
  // Inlined rather than <img>, so the diagram follows the page's light/dark theme.
  fetch("/architecture.svg")
    .then((r) => r.text())
    .then((svg) => { $("#arch-diagram").innerHTML = svg; })
    .catch(() => { $("#arch-diagram").innerHTML = `<div class="empty">diagram unavailable</div>`; });
}

/* ── health ────────────────────────────────────────────────── */
async function loadHealth() {
  try {
    const h = await api("/api/health");
    $("#status-chips").innerHTML = [
      `<span class="chip">${esc(h.backend)} · ${esc(h.model)}</span>`,
      `<span class="chip">${h.n_samples} samples</span>`,
      `<span class="chip ${h.db_exists ? "ok" : ""}">${h.n_runs} runs stored</span>`,
    ].join("");
  } catch (e) {
    $("#status-chips").innerHTML = `<span class="chip bad">server error</span>`;
  }
}

/* ── dataset ───────────────────────────────────────────────── */
async function loadDataset() {
  const data = await api("/api/dataset?limit=1000");
  state.samples = data.samples;
  state.stats = data.stats || {};
  const s = state.stats;

  $("#dataset-meta").textContent = `${s.n_samples ?? state.samples.length} files`;
  $("#dataset-stats").innerHTML = statGrid([
    ["samples", s.n_samples ?? "—"],
    ["total lines", (s.total_lines ?? 0).toLocaleString()],
    ["mean lines", s.mean_lines ?? "—"],
    ["longest", s.max_lines ?? "—"],
    ["AST nodes", (s.total_ast_nodes ?? 0).toLocaleString()],
    ["nested recursion", s.with_nested_recursion ?? "—"],
    ["mutual recursion", s.with_mutual_recursion ?? "—"],
    ["train/val/test", Object.values(s.splits || {}).join(" / ") || "—"],
  ]);

  $("#depth-charts").innerHTML = ["block_depth", "loop_depth", "branch_depth"]
    .filter((k) => s[k]).map((k) =>
      `<h3>${k.replace("_", " ")}</h3>${barChart(s[k], { labelPrefix: "depth " })}`).join("");

  $("#kind-chart").innerHTML = barChart(s.unit_kinds || {});

  const selects = [$("#extract-select"), $("#hierarchy-select")];
  const options = state.samples.map((r) =>
    `<option value="${esc(r.id)}">${esc(r.id)} · ${r.n_lines} lines · depth ${r.block_depth}</option>`).join("");
  selects.forEach((sel) => { if (sel) sel.innerHTML = options; });

  renderSamples("");
}

function renderSamples(filter) {
  const rows = state.samples
    .filter((r) => !filter || r.id.includes(filter))
    .slice(0, 300)
    .map((r) => ({
      id: r.id,
      cells: [
        { html: `<code>${esc(r.id)}</code>` },
        { value: r.split },
        { value: r.n_lines, num: true },
        { value: r.block_depth, num: true },
        { value: r.loop_depth, num: true },
        { value: r.branch_depth, num: true },
        { value: r.n_functions, num: true },
        { value: r.n_classes, num: true },
      ],
    }));
  $("#samples-table").innerHTML = table(
    ["Sample", "Split", { label: "Lines", num: true }, { label: "Block", num: true },
     { label: "Loop", num: true }, { label: "Branch", num: true },
     { label: "Funcs", num: true }, { label: "Classes", num: true }], rows);

  $$("#samples-table tbody tr").forEach((tr) => tr.addEventListener("click", () => {
    $("#hierarchy-select").value = tr.dataset.id;
    $$(".tab").find((t) => t.dataset.tab === "hierarchy").click();
    loadHierarchy();
  }));
}

$("#sample-filter")?.addEventListener("input", (e) => renderSamples(e.target.value.trim()));

/* ── extract ───────────────────────────────────────────────── */
async function loadSource() {
  const id = $("#extract-select").value;
  if (!id) return;
  try {
    const data = await api(`/api/sample/${encodeURIComponent(id)}`);
    $("#extract-source").textContent = data.source.split("\n").slice(0, 160).join("\n");
    $("#extract-note").textContent = `${data.n_lines} lines · ${data.gold.scopes.length} scopes · ${data.gold.blocks.length} blocks in gold`;
  } catch (e) { toast(e.message, true); }
}

$("#extract-select")?.addEventListener("change", loadSource);

$("#extract-run")?.addEventListener("click", async () => {
  const btn = $("#extract-run");
  const id = $("#extract-select").value;
  const strategy = $("#strategy").value;
  if (!id) return toast("pick a sample", true);

  btn.disabled = true;
  btn.innerHTML = `<span class="spinner"></span>Extracting…`;
  $("#extract-result").innerHTML = `<div class="empty"><span class="spinner"></span>
    Running ${esc(strategy)} on ${esc(id)}. The multicall path makes one request per definition,
    so this takes a while on a slow backend.</div>`;
  try {
    const res = await api("/api/extract", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ file_id: id, strategy }),
    });
    state.current = res;
    $("#extract-result").innerHTML = resultCard(res);
    const treeBox = document.createElement("div");
    treeBox.innerHTML = `<h3>Extracted tree</h3>${visualTree(res.tree)}`;
    $("#extract-result").appendChild(treeBox);
    bindTree(treeBox);
    toast(`${res.file_id}: overall ${res.score.overall.toFixed(3)}`);
    loadHealth();
  } catch (e) {
    $("#extract-result").innerHTML = `<div class="empty">Failed: ${esc(e.message)}</div>`;
    toast(e.message, true);
  } finally {
    btn.disabled = false;
    btn.textContent = "Extract";
  }
});

/* ── hierarchy ─────────────────────────────────────────────── */
let hierarchyData = null;
let hierarchyView = "diagram";
// `ready` rather than checking collapsed.size: an empty set is a legitimate state
// ("expand everything"), and treating it as "not initialised" re-folded the tree instantly.
const dg = { collapsed: new Set(), zoom: 1, ready: false };

async function loadHierarchy() {
  const id = $("#hierarchy-select").value;
  if (!id) return;
  $("#hierarchy-body").innerHTML = `<div class="empty"><span class="spinner"></span>loading…</div>`;
  try {
    hierarchyData = await api(`/api/sample/${encodeURIComponent(id)}`);
    dg.collapsed = new Set();   // a new file gets the default fold, not the last file's
    dg.ready = false;
    $("#hierarchy-meta").textContent =
      `${hierarchyData.gold.scopes.length} scopes · ${hierarchyData.gold.blocks.length} blocks · ` +
      `${hierarchyData.gold.relations.length} relations · ground truth`;
    paintHierarchy();
  } catch (e) {
    $("#hierarchy-body").innerHTML = `<div class="empty">${esc(e.message)}</div>`;
  }
}

function paintHierarchy() {
  if (!hierarchyData) return;
  const body = $("#hierarchy-body");
  if (hierarchyView === "diagram") {
    if (!dg.ready) {
      dg.collapsed = collapseDefaults(hierarchyData.tree.root, "scopes");
      dg.ready = true;
    }
    body.innerHTML = treeDiagram(hierarchyData.tree, dg.collapsed);
    bindDiagram(body, hierarchyData.tree, dg, paintHierarchy);
  } else if (hierarchyView === "visual") {
    body.innerHTML = visualTree(hierarchyData.tree);
    bindTree(body);
  } else if (hierarchyView === "tree") {
    body.innerHTML = `<div class="tree">${scopeTree(hierarchyData.hierarchy)}</div>`;
  } else if (hierarchyView === "ascii") {
    body.innerHTML = `<pre class="code">${esc(hierarchyData.tree_text || "")}</pre>`;
  } else if (hierarchyView === "outline") {
    body.innerHTML = `<pre class="code">${esc(hierarchyData.outline)}</pre>`;
  } else {
    body.innerHTML = jsonBlock(hierarchyData.tree);
  }
}

$("#hierarchy-select")?.addEventListener("change", loadHierarchy);
$$("#hierarchy-view button").forEach((b) => b.addEventListener("click", () => {
  $$("#hierarchy-view button").forEach((x) => x.classList.remove("is-active"));
  b.classList.add("is-active");
  hierarchyView = b.dataset.view;
  paintHierarchy();
}));

/* ── evaluation ────────────────────────────────────────────── */
async function loadMetrics() {
  try {
    const data = await api("/api/metrics");
    state.metrics = data.runs;
    if (!state.metrics.length) {
      $("#eval-body").innerHTML = `<div class="empty">No runs yet. Try
        <code>python3 scripts/run_code_pipeline.py --count 20</code></div>`;
      return;
    }
    $("#eval-run").innerHTML = state.metrics.map((m, i) =>
      `<option value="${i}">${esc(m.file)} · ${esc(m.strategy)} · ${m.count} files</option>`).join("");
    paintMetrics(0);
  } catch (e) { $("#eval-body").innerHTML = `<div class="empty">${esc(e.message)}</div>`; }
}

function paintMetrics(index) {
  const m = state.metrics[index];
  if (!m) return;
  $("#eval-meta").textContent = `${m.count} files · ${esc(m.strategy)} · ${(m.elapsed_s / 60).toFixed(1)} min`;
  const rows = (m.per_file || []).map((r) => ({
    cells: [
      { html: `<code>${esc(r.id)}</code>` },
      { html: r.valid ? `<span class="badge ok">valid</span>` : `<span class="badge bad">${r.n_errors}</span>` },
      { value: (r.scope_f1 ?? 0).toFixed(3), num: true },
      { value: (r.kind_accuracy ?? 0).toFixed(3), num: true },
      { value: (r.parent_accuracy ?? 0).toFixed(3), num: true },
      { value: (r.relation_f1 ?? 0).toFixed(3), num: true },
      { value: (r.depth_mae ?? 0).toFixed(2), num: true },
      { value: (r.overall ?? 0).toFixed(3), num: true },
      { value: `${(r.elapsed_s ?? 0).toFixed(0)}s`, num: true },
    ],
  }));
  $("#eval-body").innerHTML = metricGrid(m.aggregate || {}) +
    `<h3>Per file</h3><div class="table-wrap"><table class="table">` +
    table(["Sample", "Valid", { label: "Scope F1", num: true }, { label: "Kind", num: true },
           { label: "Parent", num: true }, { label: "Rel F1", num: true },
           { label: "Depth MAE", num: true }, { label: "Overall", num: true },
           { label: "Time", num: true }], rows) + `</table></div>` +
    (m.failures?.length ? `<h3>Failures</h3><ul class="issues">${
      m.failures.map((f) => `<li class="err">${esc(f.id)}: ${esc(f.error)}</li>`).join("")}</ul>` : "");
}

$("#eval-run")?.addEventListener("change", (e) => paintMetrics(Number(e.target.value)));
$("#eval-refresh")?.addEventListener("click", loadMetrics);

/* ── history ───────────────────────────────────────────────── */
async function loadHistory() {
  try {
    const { runs } = await api("/api/runs?limit=80");
    $("#history-db").textContent = `${runs.length} runs`;
    $("#history-table").innerHTML = table(
      [{ label: "#", num: true }, "File", "Model", "Valid",
       { label: "Overall", num: true }, { label: "Time", num: true }, "When"],
      runs.map((r) => ({
        id: String(r.id),
        cells: [
          { value: r.id, num: true },
          { html: `<code>${esc(r.file_id)}</code>` },
          { html: `<code>${esc(r.model_name)}</code>` },
          { html: r.is_valid ? `<span class="badge ok">valid</span>`
                             : `<span class="badge bad">${(r.validation_errors || []).length}</span>` },
          { value: (r.overall ?? 0).toFixed(3), num: true },
          { value: `${(r.elapsed_s ?? 0).toFixed(0)}s`, num: true },
          { value: r.created_at },
        ],
      })));
    $$("#history-table tbody tr").forEach((tr) => tr.addEventListener("click", () => showRun(tr.dataset.id)));
  } catch (e) { $("#history-table").innerHTML = `<tbody><tr><td>${esc(e.message)}</td></tr></tbody>`; }
}

$("#history-refresh")?.addEventListener("click", loadHistory);

async function showRun(id) {
  try {
    const data = await api(`/api/run/${id}`);
    $("#detail-title").textContent = `Run ${id} · ${data.run?.file_id ?? ""}`;
    $("#detail-body").innerHTML =
      `<div class="metricgrid">${metricGrid(flattenScore(data.run?.score || {}))}</div>` +
      `<h3>Hierarchy</h3><div class="tree">${scopeTree(data.hierarchy)}</div>` +
      `<h3>Record</h3>${jsonBlock(data.record)}`;
    $("#detail").showModal();
  } catch (e) { toast(e.message, true); }
}

function flattenScore(s) {
  return {
    scope_f1: s.scopes?.f1, kind_accuracy: s.kind_accuracy, parent_accuracy: s.parent_accuracy,
    relation_f1: s.relations?.f1, recursive_f1: s.recursive_flags?.f1,
    generator_f1: s.generator_flags?.f1, entrypoint_f1: s.entrypoints?.f1,
    overall: s.overall, depth_mae: s.max_block_depth?.mae,
  };
}

$("#detail-close")?.addEventListener("click", () => $("#detail").close());

/* ── boot ──────────────────────────────────────────────────── */
renderDocs();
loadHealth();
loadDataset().then(() => { loadSource(); }).catch((e) => toast(e.message, true));
