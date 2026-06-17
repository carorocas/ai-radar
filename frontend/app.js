const SNAPSHOT_PATH = "../data/daily/2026-06-10-ai-signals.json";
const SOURCES_PATH = "../config/sources.json";

const state = {
  mode: "reader",
  snapshot: null,
  sourcesConfig: null,
  signals: [],
  filtered: [],
  filters: {
    search: "",
    date: "all",
    source: "all",
    status: "all",
    sort: "status",
  },
};

const statusPriority = {
  riesgo_alto: 5,
  vigilar_infraestructura: 4,
  probar_pronto: 3,
  vigilar: 2,
  esperar_para_probar: 1,
};

const els = {
  stateMessage: document.querySelector("#stateMessage"),
  stateDot: document.querySelector(".state-dot"),
  filtersForm: document.querySelector("#filtersForm"),
  controlPanel: document.querySelector("#controlPanel"),
  searchInput: document.querySelector("#searchInput"),
  dateFilter: document.querySelector("#dateFilter"),
  sourceFilter: document.querySelector("#sourceFilter"),
  statusFilter: document.querySelector("#statusFilter"),
  sortFilter: document.querySelector("#sortFilter"),
  signalsBody: document.querySelector("#signalsBody"),
  emptyState: document.querySelector("#emptyState"),
  resultCount: document.querySelector("#resultCount"),
  signalsMetric: document.querySelector("#signalsMetric"),
  sourcesMetric: document.querySelector("#sourcesMetric"),
  sourcesMode: document.querySelector("#sourcesMode"),
  snapshotMetric: document.querySelector("#snapshotMetric"),
  summaryCount: document.querySelector("#summaryCount"),
  validateButton: document.querySelector("#validateButton"),
  saveButton: document.querySelector("#saveButton"),
};

function syncControlPanel() {
  if (window.matchMedia("(max-width: 720px)").matches) {
    els.controlPanel.removeAttribute("open");
  } else {
    els.controlPanel.setAttribute("open", "");
  }
}

function setBanner(type, message) {
  els.stateDot.classList.toggle("is-loading", type === "loading");
  els.stateDot.classList.toggle("is-error", type === "error");
  els.stateMessage.textContent = message;
}

function normalizeHost(url) {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return "fuente sin host";
  }
}

function inferSourceType(signal) {
  const name = signal.source.name.toLowerCase();
  const url = signal.source.url.toLowerCase();
  if (url.includes("github.com")) return "repo_tecnico";
  if (name.includes("hacker") || name.includes("reddit") || name.includes("hugging")) return "comunidad";
  if (name.includes("ap") || name.includes("techcrunch") || name.includes("times") || name.includes("verge")) {
    return "medio_secundario";
  }
  return "fuente_oficial";
}

function sourceChipClass(type) {
  if (type === "repo_tecnico") return "repo";
  if (type === "comunidad") return "community";
  if (type === "medio_secundario") return "community";
  return "official";
}

function impactLevel(impact) {
  const text = impact.toLowerCase();
  if (text.includes("muy alto") || text.includes("alto")) return "high";
  if (text.includes("medio")) return "medium";
  return "low";
}

function impactLabel(impact) {
  const level = impactLevel(impact);
  if (level === "high") return "Alto";
  if (level === "medium") return "Medio";
  return "Bajo";
}

function actionLabel(signal) {
  if (signal.status === "riesgo_alto") return "Validar contrato";
  if (signal.status === "probar_pronto") return "Probar en staging";
  if (signal.status === "vigilar_infraestructura") return "Evaluar impacto";
  return "Monitorear";
}

function scoreLabel(signal) {
  if (Number.isFinite(signal.importance_score)) {
    return String(signal.importance_score);
  }
  return "Sin puntaje";
}

function sortSignals(signals) {
  const sorted = [...signals];
  if (state.filters.sort === "newest") {
    return sorted.sort((a, b) => b.source.published_at.localeCompare(a.source.published_at));
  }
  if (state.filters.sort === "title") {
    return sorted.sort((a, b) => a.title.localeCompare(b.title, "es"));
  }
  return sorted.sort((a, b) => {
    const priority = (statusPriority[b.status] || 0) - (statusPriority[a.status] || 0);
    if (priority !== 0) return priority;
    return b.source.published_at.localeCompare(a.source.published_at);
  });
}

function applyFilters() {
  const search = state.filters.search.trim().toLowerCase();
  const filtered = state.signals.filter((signal) => {
    const sourceType = inferSourceType(signal);
    const text = [signal.title, signal.evidence, signal.impact, signal.action, signal.source.name]
      .join(" ")
      .toLowerCase();
    const matchesSearch = !search || text.includes(search);
    const matchesDate = state.filters.date === "all" || signal.source.published_at === state.filters.date;
    const matchesSource = state.filters.source === "all" || sourceType === state.filters.source;
    const matchesStatus = state.filters.status === "all" || signal.status === state.filters.status;
    return matchesSearch && matchesDate && matchesSource && matchesStatus;
  });

  state.filtered = sortSignals(filtered);
  render();
}

function createEvidence(signal) {
  const type = inferSourceType(signal);
  const chips = [
    ["oficial", type === "fuente_oficial" ? "1" : "0"],
    ["tecnica", type === "repo_tecnico" ? "1" : "0"],
    ["comunidad", type === "comunidad" ? "1" : "0"],
  ];
  return chips
    .map(([label, count]) => `<span class="evidence-chip"><strong>${count}</strong> ${label}</span>`)
    .join("");
}

function signalRow(signal, index) {
  const type = inferSourceType(signal);
  const chipClass = sourceChipClass(type);
  const impact = impactLevel(signal.impact);
  return `
    <tr>
      <td data-label="#"><span class="rank">${index + 1}</span></td>
      <td data-label="Score"><span class="score">${scoreLabel(signal)}</span></td>
      <td data-label="Senal">
        <p class="signal-title">${escapeHtml(signal.title)}</p>
        <p class="signal-copy">${escapeHtml(signal.evidence)}</p>
        <span class="operator-only evidence-chip">id: ${escapeHtml(signal.id)}</span>
      </td>
      <td data-label="Fuente" class="source-cell">
        <span class="chip ${chipClass}">${type}</span>
        <a href="${signal.source.url}" target="_blank" rel="noreferrer">${escapeHtml(normalizeHost(signal.source.url))}</a>
      </td>
      <td data-label="Evidencia">
        <div class="evidence-list">${createEvidence(signal)}</div>
      </td>
      <td data-label="Impacto"><span class="impact-pill ${impact}">${impactLabel(signal.impact)}</span></td>
      <td data-label="Accion"><button class="action-button" type="button">${actionLabel(signal)}</button></td>
      <td data-label="Estado">
        <span class="status-pill ${signal.status}">${signal.status}</span>
        <span class="date-meta">${signal.source.published_at}</span>
      </td>
    </tr>
  `;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function render() {
  els.signalsBody.innerHTML = state.filtered.map(signalRow).join("");
  els.emptyState.hidden = state.filtered.length !== 0;
  els.resultCount.textContent = `${state.filtered.length} senales encontradas`;
  els.signalsMetric.textContent = String(state.filtered.length);
  els.summaryCount.textContent = `${state.filtered.length} senales`;
}

function fillSelect(select, values, formatter = (value) => value) {
  const current = select.value;
  const first = select.querySelector("option")?.outerHTML || "";
  select.innerHTML = first + values.map((value) => `<option value="${value}">${formatter(value)}</option>`).join("");
  if ([...select.options].some((option) => option.value === current)) {
    select.value = current;
  }
}

function populateControls() {
  const dates = [...new Set(state.signals.map((signal) => signal.source.published_at))].sort().reverse();
  const sourceTypes = [...new Set(state.signals.map(inferSourceType))].sort();
  const statuses = [...new Set(state.signals.map((signal) => signal.status))].sort();

  els.dateFilter.innerHTML = `<option value="all">Todas</option>`;
  fillSelect(els.dateFilter, dates);
  fillSelect(els.sourceFilter, sourceTypes);
  fillSelect(els.statusFilter, statuses);
}

function updateMetrics() {
  const sources = new Set(state.signals.map((signal) => signal.source.url));
  els.sourcesMetric.textContent = String(sources.size);
  els.sourcesMode.textContent = state.sourcesConfig ? "Notion cache local" : "JSON snapshot";
  els.snapshotMetric.textContent = state.snapshot ? state.snapshot.date : "Sin snapshot";
}

async function loadJson(path) {
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`No se pudo cargar ${path}: ${response.status}`);
  }
  return response.json();
}

async function loadApp() {
  setBanner("loading", "Cargando senales desde JSON snapshot...");
  try {
    const [snapshot, sourcesResult] = await Promise.allSettled([
      loadJson(SNAPSHOT_PATH),
      loadJson(SOURCES_PATH),
    ]);

    if (snapshot.status !== "fulfilled") {
      throw snapshot.reason;
    }

    state.snapshot = snapshot.value;
    state.signals = Array.isArray(state.snapshot.signals) ? state.snapshot.signals : [];
    if (!state.signals.length) {
      setBanner("success", "Snapshot cargado, pero no contiene senales.");
    } else {
      setBanner("success", `Snapshot real cargado: ${state.snapshot.date}.`);
    }

    if (sourcesResult.status === "fulfilled") {
      state.sourcesConfig = sourcesResult.value;
    } else {
      setBanner("success", "Snapshot cargado. Fuentes Notion cache no disponible; usando fuentes del snapshot.");
    }

    populateControls();
    updateMetrics();
    applyFilters();
  } catch (error) {
    console.error(error);
    state.signals = [];
    state.filtered = [];
    render();
    setBanner("error", "Error al cargar datos reales. Revisa que el servidor este en la raiz de codex.");
  }
}

document.querySelectorAll(".mode-button").forEach((button) => {
  button.addEventListener("click", () => {
    state.mode = button.dataset.mode;
    document.body.classList.toggle("operator-mode", state.mode === "operator");
    document.querySelectorAll(".mode-button").forEach((item) => {
      const active = item === button;
      item.classList.toggle("is-active", active);
      item.setAttribute("aria-pressed", String(active));
    });
  });
});

els.filtersForm.addEventListener("input", () => {
  state.filters.search = els.searchInput.value;
  state.filters.date = els.dateFilter.value;
  state.filters.source = els.sourceFilter.value;
  state.filters.status = els.statusFilter.value;
  applyFilters();
});

els.sortFilter.addEventListener("change", () => {
  state.filters.sort = els.sortFilter.value;
  applyFilters();
});

els.validateButton.addEventListener("click", () => {
  setBanner("success", "Validacion disponible por CLI: python codex\\scripts\\validate_contracts.py");
});

els.saveButton.addEventListener("click", () => {
  setBanner("success", "Guardado disponible por CLI: python codex\\scripts\\save_signals.py --input codex\\data\\daily\\2026-06-10-ai-signals.json");
});

window.addEventListener("resize", syncControlPanel);
syncControlPanel();
loadApp();
