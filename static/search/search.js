/* AtlasPI Advanced Search — v6.19 */
(function () {
  "use strict";

  // ─── State ──────────────────────────────────────────────────
  const state = {
    query: "",
    dataType: null,       // null = all
    entityType: null,
    yearMin: null,
    yearMax: null,
    status: null,
    confidenceMin: null,
    confidenceMax: null,
    sort: "relevance",
    limit: 30,
    offset: 0,
    view: "cards",        // "cards" or "list"
    results: [],
    total: 0,
    loading: false,
    typeCounts: { entity: 0, event: 0, city: 0, route: 0 },
  };

  // ─── DOM refs ───────────────────────────────────────────────
  const $ = (s) => document.querySelector(s);
  const $$ = (s) => document.querySelectorAll(s);

  const searchInput = $("#s-search-input");
  const yearMinInput = $("#s-year-min");
  const yearMaxInput = $("#s-year-max");
  const confMinInput = $("#s-conf-min");
  const confMaxInput = $("#s-conf-max");
  const sortSelect = $("#s-sort");
  const resultsContainer = $("#s-results");
  const listContainer = $("#s-list-body");
  const cardsContainer = $("#s-cards");
  const listWrapper = $("#s-list-wrapper");
  const resultsCount = $("#s-results-count");
  const pagination = $("#s-pagination");
  const emptyState = $("#s-empty");
  const loadingState = $("#s-loading");

  // ─── Init from URL ──────────────────────────────────────────
  function initFromUrl() {
    const params = new URLSearchParams(window.location.search);
    if (params.get("q")) {
      state.query = params.get("q");
      searchInput.value = state.query;
    }
    if (params.get("type")) state.dataType = params.get("type");
    if (params.get("entity_type")) state.entityType = params.get("entity_type");
    if (params.get("year_min")) state.yearMin = parseInt(params.get("year_min"));
    if (params.get("year_max")) state.yearMax = parseInt(params.get("year_max"));
    if (params.get("status")) state.status = params.get("status");
    if (params.get("sort")) state.sort = params.get("sort");

    // Restore UI
    if (state.yearMin != null) yearMinInput.value = state.yearMin;
    if (state.yearMax != null) yearMaxInput.value = state.yearMax;
    if (state.sort) sortSelect.value = state.sort;

    // Restore active chips
    if (state.dataType) {
      $$(".s-type-chip").forEach((c) => {
        if (c.dataset.type === state.dataType) c.classList.add("active");
      });
    }
    if (state.status) {
      $$(".s-status-chip").forEach((c) => {
        if (c.dataset.status === state.status) c.classList.add("active");
      });
    }
    if (state.entityType) {
      $$(".s-entity-type-chip").forEach((c) => {
        if (c.dataset.etype === state.entityType) c.classList.add("active");
      });
    }

    if (state.query) doSearch();
  }

  // ─── URL sync ───────────────────────────────────────────────
  function syncUrl() {
    const params = new URLSearchParams();
    if (state.query) params.set("q", state.query);
    if (state.dataType) params.set("type", state.dataType);
    if (state.entityType) params.set("entity_type", state.entityType);
    if (state.yearMin != null) params.set("year_min", state.yearMin);
    if (state.yearMax != null) params.set("year_max", state.yearMax);
    if (state.status) params.set("status", state.status);
    if (state.sort !== "relevance") params.set("sort", state.sort);
    const qs = params.toString();
    const url = qs ? `/search?${qs}` : "/search";
    history.replaceState(null, "", url);
  }

  // ─── Search ─────────────────────────────────────────────────
  let searchTimer = null;

  function scheduleSearch() {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      state.query = searchInput.value.trim();
      state.offset = 0;
      doSearch();
    }, 300);
  }

  async function doSearch() {
    if (!state.query) {
      showEmpty("Type a search query to explore the dataset");
      syncUrl();
      return;
    }

    state.loading = true;
    showLoading();
    syncUrl();

    const params = new URLSearchParams();
    params.set("q", state.query);
    params.set("limit", state.limit);
    params.set("offset", state.offset);
    params.set("sort", state.sort);
    if (state.dataType) params.set("data_type", state.dataType);
    if (state.entityType) params.set("entity_type", state.entityType);
    if (state.yearMin != null) params.set("year_min", state.yearMin);
    if (state.yearMax != null) params.set("year_max", state.yearMax);
    if (state.status) params.set("status", state.status);
    if (state.confidenceMin != null) params.set("confidence_min", state.confidenceMin);
    if (state.confidenceMax != null) params.set("confidence_max", state.confidenceMax);

    try {
      const res = await fetch(`/v1/search/advanced?${params}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      state.results = data.results;
      state.total = data.total;
      state.loading = false;

      // Count by type (for tabs) — use full results when not filtering by type
      if (!state.dataType) {
        state.typeCounts = { entity: 0, event: 0, city: 0, route: 0 };
        data.results.forEach((r) => {
          if (state.typeCounts[r.type] !== undefined) state.typeCounts[r.type]++;
        });
        // Total counts: total might be larger than the page, so estimate
        // We show counts for the page but indicate total
      }

      renderResults();
    } catch (err) {
      state.loading = false;
      showEmpty("Search failed. Please try again.");
      console.error("Search error:", err);
    }
  }

  // ─── Render ─────────────────────────────────────────────────
  function renderResults() {
    if (state.results.length === 0) {
      showEmpty(`No results for "${state.query}"`);
      return;
    }

    emptyState.style.display = "none";
    loadingState.style.display = "none";

    // Update tabs
    updateTabs();

    // Count text
    const from = state.offset + 1;
    const to = Math.min(state.offset + state.limit, state.total);
    resultsCount.textContent = `${state.total} result${state.total !== 1 ? "s" : ""} (showing ${from}-${to})`;

    // Cards
    cardsContainer.innerHTML = state.results.map(cardHtml).join("");

    // List
    listContainer.innerHTML = state.results.map(rowHtml).join("");

    // View
    updateView();

    // Pagination
    renderPagination();
  }

  function cardHtml(r) {
    const badge = badgeClass(r.type);
    const yearStr = formatYear(r.year_start, r.year_end);
    const conf = r.confidence_score != null ? r.confidence_score : 0;
    const confPct = Math.round(conf * 100);
    const confColor = conf >= 0.7 ? "var(--green)" : conf >= 0.4 ? "var(--yellow)" : "var(--red)";
    const hl = highlightQuery(r.highlight || r.name, state.query);
    const link = detailLink(r);

    return `<div class="s-card" onclick="window.open('${link}','_blank')">
      <div class="s-card-header">
        <div class="s-card-name">${esc(r.name)}</div>
        <span class="s-card-badge ${badge}">${r.type}</span>
      </div>
      <div class="s-card-meta">
        <span>${esc(r.subtype || "")}</span>
        <span>${yearStr}</span>
        <span>${esc(r.status || "")}</span>
      </div>
      <div class="s-card-highlight">${hl}</div>
      <div class="s-card-footer">
        <span class="s-confidence">
          Confidence: ${confPct}%
          <span class="s-confidence-bar"><span class="s-confidence-fill" style="width:${confPct}%;background:${confColor}"></span></span>
        </span>
        <span style="font-size:.75rem;color:var(--text-muted)">Score: ${r.score}</span>
      </div>
    </div>`;
  }

  function rowHtml(r) {
    const badge = badgeClass(r.type);
    const yearStr = formatYear(r.year_start, r.year_end);
    const conf = r.confidence_score != null ? Math.round(r.confidence_score * 100) : 0;
    const link = detailLink(r);

    return `<tr onclick="window.open('${link}','_blank')" style="cursor:pointer">
      <td><span class="s-card-badge ${badge}" style="font-size:.65rem">${r.type}</span></td>
      <td class="s-name-cell">${esc(r.name)}</td>
      <td>${esc(r.subtype || "")}</td>
      <td>${yearStr}</td>
      <td>${esc(r.status || "")}</td>
      <td>${conf}%</td>
    </tr>`;
  }

  function badgeClass(type) {
    return {
      entity: "s-badge-entity",
      event: "s-badge-event",
      city: "s-badge-city",
      route: "s-badge-route",
    }[type] || "s-badge-entity";
  }

  function detailLink(r) {
    const map = {
      entity: `/v1/entities/${r.id}`,
      event: `/v1/events/${r.id}`,
      city: `/v1/cities/${r.id}`,
      route: `/v1/routes/${r.id}`,
    };
    return map[r.type] || "#";
  }

  function formatYear(start, end) {
    if (start == null) return "";
    let s = start < 0 ? `${Math.abs(start)} BCE` : `${start} CE`;
    if (end != null) {
      let e = end < 0 ? `${Math.abs(end)} BCE` : `${end} CE`;
      s += ` - ${e}`;
    }
    return s;
  }

  function highlightQuery(text, query) {
    if (!text || !query) return esc(text || "");
    const escaped = esc(text);
    const idx = escaped.toLowerCase().indexOf(query.toLowerCase());
    if (idx === -1) return escaped;
    const before = escaped.slice(0, idx);
    const match = escaped.slice(idx, idx + query.length);
    const after = escaped.slice(idx + query.length);
    return `${before}<mark>${match}</mark>${after}`;
  }

  function esc(s) {
    if (!s) return "";
    const d = document.createElement("div");
    d.textContent = String(s);
    return d.innerHTML;
  }

  // ─── Tabs ───────────────────────────────────────────────────
  function updateTabs() {
    $$(".s-tab").forEach((tab) => {
      const type = tab.dataset.type;
      const countEl = tab.querySelector(".s-tab-count");
      if (type === "all") {
        if (countEl) countEl.textContent = `(${state.total})`;
        tab.classList.toggle("active", !state.dataType);
      } else {
        const cnt = state.typeCounts[type] || 0;
        if (countEl) countEl.textContent = `(${cnt})`;
        tab.classList.toggle("active", state.dataType === type);
      }
    });
  }

  // ─── Pagination ─────────────────────────────────────────────
  function renderPagination() {
    const totalPages = Math.ceil(state.total / state.limit);
    const currentPage = Math.floor(state.offset / state.limit) + 1;

    if (totalPages <= 1) {
      pagination.innerHTML = "";
      return;
    }

    pagination.innerHTML = `
      <button class="s-page-btn" id="s-prev" ${currentPage <= 1 ? "disabled" : ""}>Prev</button>
      <span class="s-page-info">Page ${currentPage} of ${totalPages}</span>
      <button class="s-page-btn" id="s-next" ${currentPage >= totalPages ? "disabled" : ""}>Next</button>
    `;

    $("#s-prev")?.addEventListener("click", () => {
      state.offset = Math.max(0, state.offset - state.limit);
      doSearch();
    });
    $("#s-next")?.addEventListener("click", () => {
      state.offset += state.limit;
      doSearch();
    });
  }

  // ─── View toggle ────────────────────────────────────────────
  function updateView() {
    const isCards = state.view === "cards";
    cardsContainer.style.display = isCards ? "grid" : "none";
    listWrapper.style.display = isCards ? "none" : "block";
    $$(".s-view-btn").forEach((b) => {
      b.classList.toggle("active", b.dataset.view === state.view);
    });
  }

  // ─── Show states ────────────────────────────────────────────
  function showEmpty(msg) {
    cardsContainer.innerHTML = "";
    listContainer.innerHTML = "";
    pagination.innerHTML = "";
    resultsCount.textContent = "";
    loadingState.style.display = "none";
    emptyState.style.display = "block";
    emptyState.querySelector(".s-empty-text").textContent = msg || "No results";
  }

  function showLoading() {
    cardsContainer.innerHTML = "";
    listContainer.innerHTML = "";
    pagination.innerHTML = "";
    resultsCount.textContent = "";
    emptyState.style.display = "none";
    loadingState.style.display = "block";
  }

  // ─── Export ─────────────────────────────────────────────────
  function buildExportParams() {
    const params = new URLSearchParams();
    if (state.entityType) params.set("entity_type", state.entityType);
    if (state.yearMin != null) params.set("year_min", state.yearMin);
    if (state.yearMax != null) params.set("year_max", state.yearMax);
    if (state.status) params.set("status", state.status);
    if (state.confidenceMin != null) params.set("confidence_min", state.confidenceMin);
    if (state.confidenceMax != null) params.set("confidence_max", state.confidenceMax);
    return params;
  }

  function doExport(endpoint, format) {
    const params = buildExportParams();
    params.set("format", format);
    window.open(`${endpoint}?${params}`, "_blank");
  }

  // ─── Event listeners ────────────────────────────────────────
  function bindEvents() {
    // Search input
    searchInput.addEventListener("input", scheduleSearch);
    searchInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        clearTimeout(searchTimer);
        state.query = searchInput.value.trim();
        state.offset = 0;
        doSearch();
      }
    });

    // Year range
    yearMinInput.addEventListener("change", () => {
      const v = yearMinInput.value.trim();
      state.yearMin = v ? parseInt(v) : null;
      state.offset = 0;
      if (state.query) doSearch();
    });
    yearMaxInput.addEventListener("change", () => {
      const v = yearMaxInput.value.trim();
      state.yearMax = v ? parseInt(v) : null;
      state.offset = 0;
      if (state.query) doSearch();
    });

    // Confidence range
    confMinInput.addEventListener("change", () => {
      const v = confMinInput.value.trim();
      state.confidenceMin = v ? parseFloat(v) : null;
      state.offset = 0;
      if (state.query) doSearch();
    });
    confMaxInput.addEventListener("change", () => {
      const v = confMaxInput.value.trim();
      state.confidenceMax = v ? parseFloat(v) : null;
      state.offset = 0;
      if (state.query) doSearch();
    });

    // Data type tabs
    $$(".s-tab").forEach((tab) => {
      tab.addEventListener("click", () => {
        const type = tab.dataset.type;
        state.dataType = type === "all" ? null : type;
        state.offset = 0;
        if (state.query) doSearch();
      });
    });

    // Entity type chips
    $$(".s-entity-type-chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        const val = chip.dataset.etype;
        if (state.entityType === val) {
          state.entityType = null;
          chip.classList.remove("active");
        } else {
          $$(".s-entity-type-chip").forEach((c) => c.classList.remove("active"));
          state.entityType = val;
          chip.classList.add("active");
        }
        state.offset = 0;
        if (state.query) doSearch();
      });
    });

    // Status chips
    $$(".s-status-chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        const val = chip.dataset.status;
        if (state.status === val) {
          state.status = null;
          chip.classList.remove("active");
        } else {
          $$(".s-status-chip").forEach((c) => c.classList.remove("active"));
          state.status = val;
          chip.classList.add("active");
        }
        state.offset = 0;
        if (state.query) doSearch();
      });
    });

    // Sort
    sortSelect.addEventListener("change", () => {
      state.sort = sortSelect.value;
      state.offset = 0;
      if (state.query) doSearch();
    });

    // View toggle
    $$(".s-view-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        state.view = btn.dataset.view;
        updateView();
      });
    });

    // Export buttons
    $("#s-export-entities-csv")?.addEventListener("click", () => doExport("/v1/export/entities", "csv"));
    $("#s-export-entities-geojson")?.addEventListener("click", () => doExport("/v1/export/entities", "geojson"));
    $("#s-export-events-csv")?.addEventListener("click", () => doExport("/v1/export/events", "csv"));
    $("#s-export-events-json")?.addEventListener("click", () => doExport("/v1/export/events", "json"));

    // Keyboard shortcut: focus search with /
    document.addEventListener("keydown", (e) => {
      if (e.key === "/" && document.activeElement !== searchInput) {
        e.preventDefault();
        searchInput.focus();
      }
    });
  }

  // ─── Boot ───────────────────────────────────────────────────
  document.addEventListener("DOMContentLoaded", () => {
    bindEvents();
    initFromUrl();
    if (!state.query) {
      showEmpty("Type a search query to explore entities, events, cities, and trade routes");
    }
  });
})();
