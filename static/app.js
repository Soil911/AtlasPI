/* AtlasPI v2.3 — Interfaccia web */

const API = '';
const COLORS = {
  confirmed: '#3fb950',
  uncertain: '#d29922',
  disputed: '#f85149',
};

let map, layerGroup;
let allEntities = [];
let detailCache = {};
let debounceTimer = null;
let activeType = '';

// ─── Init ───────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  initMap();
  loadEntities();
  loadTypes();
  loadStats();
  bindEvents();
});

function initMap() {
  map = L.map('map', { center: [30, 20], zoom: 3, minZoom: 2, maxZoom: 12 });
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>',
    subdomains: 'abcd', maxZoom: 19,
  }).addTo(map);
  layerGroup = L.layerGroup().addTo(map);
}

// ─── API ────────────────────────────────────────────────────────

async function loadEntities() {
  try {
    const res = await fetch(`${API}/v1/entities?limit=100&offset=0`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    allEntities = data.entities;
    document.getElementById('entity-count').textContent = `${data.count} entit\u00e0`;
    applyFilters();
  } catch (err) {
    showError('Impossibile caricare i dati. Verifica che il server sia attivo.');
    document.getElementById('results-list').innerHTML =
      '<p class="placeholder">Errore di connessione</p>';
  }
}

async function loadDetail(id) {
  if (detailCache[id]) return detailCache[id];
  try {
    const res = await fetch(`${API}/v1/entities/${id}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    detailCache[id] = data;
    return data;
  } catch (err) {
    showError('Errore nel caricamento dei dettagli.');
    return null;
  }
}

async function loadTypes() {
  try {
    const res = await fetch(`${API}/v1/types`);
    if (!res.ok) return;
    const types = await res.json();
    const container = document.getElementById('type-chips');
    container.innerHTML = '<button class="chip active" data-type="">Tutti</button>' +
      types.map(t => `<button class="chip" data-type="${esc(t.type)}">${esc(t.type)} (${t.count})</button>`).join('');

    container.querySelectorAll('.chip').forEach(chip => {
      chip.addEventListener('click', () => {
        container.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        activeType = chip.dataset.type;
        applyFilters();
      });
    });
  } catch (_) {}
}

async function loadStats() {
  try {
    const res = await fetch(`${API}/v1/stats`);
    if (!res.ok) return;
    const s = await res.json();
    const bar = document.getElementById('stats-bar');
    bar.innerHTML = `
      <span class="stat-item"><span class="stat-value">${s.total_entities}</span> entit\u00e0</span>
      <span class="stat-item"><span class="stat-value">${s.total_sources}</span> fonti</span>
      <span class="stat-item"><span class="stat-value">${s.total_territory_changes}</span> cambi</span>
      <span class="stat-item"><span class="stat-value">${s.disputed_count}</span> contestati</span>
      <span class="stat-item">conf. media <span class="stat-value">${Math.round(s.avg_confidence*100)}%</span></span>
    `;
  } catch (_) {}
}

// ─── Filtri ─────────────────────────────────────────────────────

function getStatuses() {
  return Array.from(document.querySelectorAll('.checkbox-group input:checked')).map(c => c.value);
}

function applyFilters() {
  const search = document.getElementById('search-input').value.toLowerCase().trim();
  const year = parseInt(document.getElementById('year-slider').value, 10);
  const statuses = getStatuses();
  const sortVal = document.getElementById('sort-select').value;

  let filtered = allEntities.filter(e => {
    if (!statuses.includes(e.status)) return false;
    if (e.year_start > year) return false;
    if (e.year_end !== null && e.year_end < year) return false;
    if (activeType && e.entity_type !== activeType) return false;
    if (search) {
      const inOrig = e.name_original.toLowerCase().includes(search);
      const inVar = (e.name_variants || []).some(v => v.name.toLowerCase().includes(search));
      if (!inOrig && !inVar) return false;
    }
    return true;
  });

  // Sorting
  if (sortVal === 'name') {
    filtered.sort((a, b) => a.name_original.localeCompare(b.name_original));
  } else if (sortVal === 'year_start') {
    filtered.sort((a, b) => a.year_start - b.year_start);
  } else if (sortVal === 'confidence-desc') {
    filtered.sort((a, b) => b.confidence_score - a.confidence_score);
  }

  renderResults(filtered);
  renderMap(filtered);
}

// ─── Lista risultati ────────────────────────────────────────────

function renderResults(entities) {
  const el = document.getElementById('results-list');
  if (!entities.length) {
    el.innerHTML = '<p class="placeholder">Nessuna entit\u00e0 trovata per i filtri selezionati</p>';
    return;
  }

  el.innerHTML = entities.map(e => {
    const pct = Math.round(e.confidence_score * 100);
    const real = isReal(e);
    return `
    <div class="result-card ${e.status}" data-id="${e.id}" role="listitem" tabindex="0">
      <div class="name">${esc(e.name_original)}${real ? '' : ' <span class="precision-tag approx">~</span>'}</div>
      <div class="meta">
        ${e.entity_type} &middot;
        ${fmtY(e.year_start)}\u2013${e.year_end ? fmtY(e.year_end) : 'oggi'} &middot;
        <span class="status-badge ${e.status}">${e.status}</span>
        &middot; ${pct}%
      </div>
      <div class="score-bar"><div class="score-fill" style="width:${pct}%;background:${COLORS[e.status]}"></div></div>
    </div>`;
  }).join('');

  el.querySelectorAll('.result-card').forEach(card => {
    const handler = () => showDetail(+card.dataset.id);
    card.addEventListener('click', handler);
    card.addEventListener('keydown', ev => { if (ev.key === 'Enter') handler(); });
  });
}

// ─── Mappa ──────────────────────────────────────────────────────

function renderMap(entities) {
  layerGroup.clearLayers();
  entities.forEach(e => {
    if (!e.boundary_geojson) return;
    const c = COLORS[e.status] || '#8b949e';
    try {
      const geo = e.boundary_geojson;
      if (geo.type === 'Point') {
        const [lon, lat] = geo.coordinates;
        const m = L.circleMarker([lat, lon], {
          radius: 8, fillColor: c, color: '#fff', weight: 1.5, fillOpacity: 0.85,
        });
        m.bindTooltip(tip(e), { direction: 'top' });
        m.on('click', () => showDetail(e.id));
        layerGroup.addLayer(m);
      } else {
        const real = isReal(e);
        const layer = L.geoJSON(geo, {
          style: {
            fillColor: c, fillOpacity: real ? 0.18 : 0.10,
            color: c, weight: real ? 2 : 1.5,
            dashArray: e.status === 'disputed' ? '6,4' : (real ? null : '4,3'),
            opacity: real ? 0.8 : 0.5,
          },
        });
        layer.bindTooltip(tip(e), { sticky: true });
        layer.on('click', () => showDetail(e.id));
        layerGroup.addLayer(layer);

        const center = layer.getBounds().getCenter();
        layerGroup.addLayer(L.marker(center, {
          icon: L.divIcon({
            className: '',
            html: `<div style="color:${c};font-size:11px;font-weight:600;text-shadow:0 0 4px #000,0 0 2px #000;white-space:nowrap;pointer-events:none">${esc(e.name_original)}</div>`,
            iconSize: null, iconAnchor: [0, 0],
          }),
          interactive: false,
        }));
      }
    } catch (_) {}
  });
}

function tip(e) {
  return `<strong>${esc(e.name_original)}</strong><br>${e.entity_type} &middot; ${fmtY(e.year_start)}\u2013${e.year_end ? fmtY(e.year_end) : 'oggi'}<br>Affidabilit\u00e0: ${Math.round(e.confidence_score*100)}% &middot; <em>${e.status}</em>`;
}

// ─── Dettaglio ──────────────────────────────────────────────────

async function showDetail(id) {
  const panel = document.getElementById('detail-panel');
  const content = document.getElementById('detail-content');
  panel.classList.remove('hidden');
  content.innerHTML = '<div class="detail-spinner"><div class="spinner"></div></div>';

  // Collapse sidebar on mobile
  if (window.innerWidth <= 768) {
    document.getElementById('sidebar').classList.add('collapsed');
  }

  const info = document.getElementById('map-info');
  if (info) info.style.display = 'none';

  const e = await loadDetail(id);
  if (!e) { panel.classList.add('hidden'); return; }

  const pct = Math.round(e.confidence_score * 100);
  const sc = COLORS[e.status] || '#8b949e';
  const real = isReal(e);

  content.innerHTML = `
    <h2>${esc(e.name_original)}</h2>
    <span class="lang-tag">${e.name_original_lang}</span>
    <span class="status-badge ${e.status}">${e.status}</span>

    <div class="detail-section">
      <h3>Informazioni</h3>
      <p><strong>Tipo:</strong> ${e.entity_type}</p>
      <p><strong>Periodo:</strong> ${fmtY(e.year_start)} \u2013 ${e.year_end ? fmtY(e.year_end) : 'presente'}</p>
      ${e.capital ? `<p><strong>Capitale:</strong> ${esc(e.capital.name)}</p>` : ''}
    </div>

    <div class="detail-section">
      <h3>Affidabilit\u00e0</h3>
      <div class="confidence-bar"><div class="confidence-fill" style="width:${pct}%;background:${sc}"></div></div>
      <p style="font-size:0.78em;color:var(--text-muted);margin-top:4px">
        Score: ${e.confidence_score.toFixed(2)} / 1.00
        ${e.confidence_score < 0.6 ? ' \u2014 <span style="color:var(--uncertain)">dati parziali o incerti</span>' : ''}
      </p>
      ${e.boundary_geojson ? (real ? `
        <div class="boundary-notice" style="border-color:rgba(63,185,80,0.3);background:rgba(63,185,80,0.08);color:var(--confirmed)">
          Confini da dataset accademici. Verificare le fonti per dettagli.
        </div>` : `
        <div class="boundary-notice">
          Confini approssimativi a scopo dimostrativo.
        </div>`) : ''}
    </div>

    ${e.name_variants.length ? `
    <div class="detail-section">
      <h3>Nomi e varianti (ETHICS-001)</h3>
      <ul>${e.name_variants.map(v => `
        <li>
          <strong>${esc(v.name)}</strong> <span class="lang-tag">${v.lang}</span>
          ${v.period_start != null ? `<span style="font-size:0.75em;color:var(--text-muted)">${fmtY(v.period_start)}\u2013${v.period_end ? fmtY(v.period_end) : '...'}</span>` : ''}
          ${v.context ? `<br><span style="font-size:0.78em;color:var(--text-muted)">${esc(v.context)}</span>` : ''}
        </li>`).join('')}
      </ul>
    </div>` : ''}

    ${e.territory_changes.length ? `
    <div class="detail-section">
      <h3>Cambiamenti territoriali (ETHICS-002)</h3>
      <ul>${e.territory_changes.map(tc => `
        <li>
          <span class="change-type ${tc.change_type}">${tc.change_type.replace(/_/g, ' ')}</span>
          <strong>${fmtY(tc.year)}</strong> \u2014 ${esc(tc.region)}
          <span style="font-size:0.7em;color:var(--text-muted)">(${Math.round(tc.confidence_score*100)}%)</span>
          ${tc.description ? `<br><span style="font-size:0.8em">${esc(tc.description)}</span>` : ''}
          ${tc.population_affected ? `<br><span style="font-size:0.75em;color:var(--uncertain)">Popolazione colpita: ~${tc.population_affected.toLocaleString('it-IT')}</span>` : ''}
        </li>`).join('')}
      </ul>
    </div>` : ''}

    ${e.sources.length ? `
    <div class="detail-section">
      <h3>Fonti</h3>
      <ul>${e.sources.map(s => `
        <li>${esc(s.citation)} <span class="lang-tag">${s.source_type}</span></li>`).join('')}
      </ul>
    </div>` : ''}

    ${e.ethical_notes ? `
    <div class="detail-section">
      <h3>Governance etica</h3>
      <div class="ethics-box">${esc(e.ethical_notes)}</div>
    </div>` : ''}
  `;

  // Zoom
  if (e.boundary_geojson) {
    try {
      if (e.boundary_geojson.type === 'Point') {
        const [lon, lat] = e.boundary_geojson.coordinates;
        map.setView([lat, lon], 6, { animate: true });
      } else {
        map.fitBounds(L.geoJSON(e.boundary_geojson).getBounds(), { padding: [50, 50], animate: true });
      }
    } catch (_) {}
  }
}

function closeDetail() {
  document.getElementById('detail-panel').classList.add('hidden');
  const info = document.getElementById('map-info');
  if (info) info.style.display = '';
}

// ─── Error toast ────────────────────────────────────────────────

function showError(msg) {
  const toast = document.getElementById('error-toast');
  document.getElementById('error-message').textContent = msg;
  toast.classList.remove('hidden');
  setTimeout(() => toast.classList.add('hidden'), 8000);
}

// ─── Events ─────────────────────────────────────────────────────

function bindEvents() {
  const searchInput = document.getElementById('search-input');
  const yearSlider = document.getElementById('year-slider');
  const yearDisplay = document.getElementById('year-display');

  document.getElementById('search-btn').addEventListener('click', applyFilters);
  searchInput.addEventListener('keyup', e => { if (e.key === 'Enter') applyFilters(); });

  // Debounced live search
  searchInput.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(applyFilters, 300);
  });

  yearSlider.addEventListener('input', () => {
    yearDisplay.textContent = fmtY(+yearSlider.value);
  });
  yearSlider.addEventListener('change', applyFilters);

  document.querySelectorAll('.checkbox-group input').forEach(cb => {
    cb.addEventListener('change', applyFilters);
  });

  document.getElementById('sort-select').addEventListener('change', applyFilters);

  document.getElementById('reset-btn').addEventListener('click', () => {
    searchInput.value = '';
    yearSlider.value = 1500;
    yearDisplay.textContent = '1500';
    document.querySelectorAll('.checkbox-group input').forEach(cb => { cb.checked = true; });
    document.getElementById('sort-select').value = '';
    activeType = '';
    document.querySelectorAll('#type-chips .chip').forEach(c => c.classList.remove('active'));
    const allChip = document.querySelector('#type-chips .chip[data-type=""]');
    if (allChip) allChip.classList.add('active');
    applyFilters();
    closeDetail();
  });

  document.getElementById('close-detail').addEventListener('click', closeDetail);
  document.getElementById('error-dismiss').addEventListener('click', () => {
    document.getElementById('error-toast').classList.add('hidden');
  });

  // Mobile sidebar toggle
  const toggle = document.getElementById('sidebar-toggle');
  const sidebar = document.getElementById('sidebar');
  if (toggle) {
    toggle.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
      toggle.setAttribute('aria-expanded', !sidebar.classList.contains('collapsed'));
    });
  }
}

// ─── Utility ────────────────────────────────────────────────────

function fmtY(y) { return y < 0 ? `${Math.abs(y)} a.C.` : String(y); }

function esc(s) {
  if (!s) return '';
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

function isReal(e) {
  if (!e.boundary_geojson) return false;
  const g = e.boundary_geojson;
  let pts = 0;
  if (g.type === 'Polygon') pts = g.coordinates.reduce((s, r) => s + r.length, 0);
  else if (g.type === 'MultiPolygon') pts = g.coordinates.reduce((s, p) => s + p.reduce((s2, r) => s2 + r.length, 0), 0);
  return pts > 50;
}
