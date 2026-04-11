/* AtlasPI v5.5.1 — Interfaccia web con deep linking e keyboard nav */

const API = '';
const COLORS = {
  confirmed: '#3fb950',
  uncertain: '#d29922',
  disputed: '#f85149',
};

const TYPE_ICONS = {
  empire: '👑',
  kingdom: '🏰',
  'city-state': '🏛️',
  colony: '⚓',
  disputed_territory: '⚠️',
  confederation: '🤝',
  caliphate: '☪️',
  republic: '🏛️',
  shogunate: '⚔️',
  dynasty: '🐉',
  sultanate: '🕌',
  khanate: '🏇',
  principality: '🏴',
  duchy: '🛡️',
  federation: '🌐',
  city: '🏙️',
};

let map, layerGroup;
let allEntities = [];
let detailCache = {};
let debounceTimer = null;
let activeType = '';
let activeContinent = '';
let selectedCardIndex = -1;
let playbackInterval = null;
let compareEntityId = null;

const CONTINENT_ICONS = {
  'Europe': '🇪🇺',
  'Asia': '🌏',
  'Africa': '🌍',
  'Americas': '🌎',
  'Middle East': '🕌',
  'Oceania': '🏝️',
  'Unknown': '❓',
  'Other': '🌐',
};

// ─── Init ───────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  initMap();
  loadEntities().then(() => restoreUrlState());
  loadTypes();
  loadContinents();
  loadStats();
  loadTimeline();
  bindEvents();
  initLang();
});

function initMap() {
  map = L.map('map', {
    center: [30, 20],
    zoom: 3,
    minZoom: 2,
    maxZoom: 12,
    scrollWheelZoom: false,   // prevent scroll-hijack on page scroll
    zoomControl: true,
  });
  // Enable scroll-zoom only after the user clicks on the map
  let scrollHintTimer = null;
  const scrollHint = document.getElementById('map-scroll-hint');

  map.on('click', () => { map.scrollWheelZoom.enable(); if (scrollHint) scrollHint.classList.remove('visible'); });
  map.on('focus', () => { map.scrollWheelZoom.enable(); });
  map.on('mouseout', () => { map.scrollWheelZoom.disable(); });

  // Show hint when user tries to scroll on map without clicking first
  document.getElementById('map').addEventListener('wheel', (ev) => {
    if (!map.scrollWheelZoom.enabled()) {
      if (scrollHint) {
        scrollHint.classList.add('visible');
        clearTimeout(scrollHintTimer);
        scrollHintTimer = setTimeout(() => scrollHint.classList.remove('visible'), 2000);
      }
    }
  }, { passive: true });

  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>',
    subdomains: 'abcd', maxZoom: 19,
  }).addTo(map);
  layerGroup = L.layerGroup().addTo(map);
}

// ─── URL State Management ──────────────────────────────────────

function getUrlState() {
  const params = new URLSearchParams(window.location.search);
  return {
    entity: params.get('entity') ? parseInt(params.get('entity'), 10) : null,
    year: params.get('year') ? parseInt(params.get('year'), 10) : null,
    search: params.get('q') || null,
    type: params.get('type') || null,
    continent: params.get('continent') || null,
    lang: params.get('lang') || null,
  };
}

function pushUrlState(opts = {}) {
  const params = new URLSearchParams();
  const year = parseInt(document.getElementById('year-slider').value, 10);
  const search = document.getElementById('search-input').value.trim();

  if (year !== 1500) params.set('year', year);
  if (search) params.set('q', search);
  if (activeType) params.set('type', activeType);
  if (activeContinent) params.set('continent', activeContinent);
  if (opts.entity) params.set('entity', opts.entity);
  if (lang !== 'it') params.set('lang', lang);

  const url = params.toString() ? `?${params.toString()}` : window.location.pathname;
  history.replaceState(null, '', url);
}

function restoreUrlState() {
  const state = getUrlState();
  let changed = false;

  if (state.lang && state.lang !== lang) {
    lang = state.lang;
    localStorage.setItem('atlaspi-lang', lang);
    applyLangUI();
  }

  if (state.year !== null) {
    const slider = document.getElementById('year-slider');
    const input = document.getElementById('year-input');
    const era = document.getElementById('year-era');
    slider.value = state.year;
    document.getElementById('year-display').textContent = fmtY(state.year);
    if (state.year < 0) {
      input.value = Math.abs(state.year);
      era.value = 'bc';
    } else {
      input.value = state.year;
      era.value = 'ad';
    }
    changed = true;
  }

  if (state.search) {
    document.getElementById('search-input').value = state.search;
    changed = true;
  }

  if (state.type) {
    activeType = state.type;
    document.querySelectorAll('#type-chips .chip').forEach(c => {
      c.classList.toggle('active', c.dataset.type === activeType);
    });
    changed = true;
  }

  if (state.continent) {
    activeContinent = state.continent;
    document.querySelectorAll('#continent-chips .chip').forEach(c => {
      c.classList.toggle('active', c.dataset.continent === activeContinent);
    });
    changed = true;
  }

  if (changed) applyFilters();

  if (state.entity) {
    setTimeout(() => showDetail(state.entity), 300);
  }
}

// ─── API ────────────────────────────────────────────────────────

async function loadEntities() {
  try {
    // Fetch all entities with pagination (API max 100 per page)
    allEntities = [];
    let offset = 0;
    const limit = 100;
    let total = Infinity;

    while (offset < total) {
      const res = await fetch(`${API}/v1/entities?limit=${limit}&offset=${offset}`, { cache: 'no-cache' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      total = data.count;
      allEntities = allEntities.concat(data.entities);
      offset += limit;
      // Safety: avoid infinite loops
      if (data.entities.length === 0) break;
    }

    document.getElementById('entity-count').textContent = `${allEntities.length} ${t('entities')}`;
    applyFilters();
  } catch (err) {
    showError(t('error_connection') || 'Impossibile caricare i dati.');
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
    showError(t('error_detail') || 'Errore nel caricamento dei dettagli.');
    return null;
  }
}

async function loadContemporaries(id) {
  try {
    const res = await fetch(`${API}/v1/entities/${id}/contemporaries?limit=20`);
    if (!res.ok) return null;
    return await res.json();
  } catch (_) { return null; }
}

async function loadTypes() {
  try {
    const res = await fetch(`${API}/v1/types`, { cache: 'no-cache' });
    if (!res.ok) return;
    const types = await res.json();
    const container = document.getElementById('type-chips');
    container.innerHTML = `<button class="chip active" data-type="">${t('all')}</button>` +
      types.map(tp => {
        const icon = TYPE_ICONS[tp.type] || '📍';
        return `<button class="chip" data-type="${esc(tp.type)}">${icon} ${esc(tp.type)} (${tp.count})</button>`;
      }).join('');

    container.querySelectorAll('.chip').forEach(chip => {
      chip.addEventListener('click', () => {
        container.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        activeType = chip.dataset.type;
        applyFilters();
        pushUrlState();
      });
    });
  } catch (_) {}
}

async function loadContinents() {
  try {
    const res = await fetch(`${API}/v1/continents`, { cache: 'no-cache' });
    if (!res.ok) return;
    const continents = await res.json();
    const container = document.getElementById('continent-chips');
    container.innerHTML = `<button class="chip active" data-continent="">${t('all')}</button>` +
      continents.map(c => {
        const icon = CONTINENT_ICONS[c.continent] || '🌐';
        return `<button class="chip" data-continent="${esc(c.continent)}">${icon} ${esc(c.continent)} (${c.count})</button>`;
      }).join('');

    container.querySelectorAll('.chip').forEach(chip => {
      chip.addEventListener('click', () => {
        container.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        activeContinent = chip.dataset.continent;
        applyFilters();
        pushUrlState();
      });
    });
  } catch (_) {}
}

async function loadStats() {
  try {
    const res = await fetch(`${API}/v1/stats`, { cache: 'no-cache' });
    if (!res.ok) return;
    const s = await res.json();
    const bar = document.getElementById('stats-bar');
    bar.innerHTML = `
      <span class="stat-item"><span class="stat-value">${s.total_entities}</span> ${t('entities')}</span>
      <span class="stat-item"><span class="stat-value">${s.total_sources}</span> ${t('sources')}</span>
      <span class="stat-item"><span class="stat-value">${s.total_territory_changes}</span> ${t('changes')}</span>
      <span class="stat-item"><span class="stat-value">${s.disputed_count}</span> ${t('contested')}</span>
      <span class="stat-item">${t('avg_conf')} <span class="stat-value">${Math.round(s.avg_confidence*100)}%</span></span>
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
    if (activeContinent && e.continent !== activeContinent) return false;
    if (search) {
      const inOrig = e.name_original.toLowerCase().includes(search);
      const inVar = (e.name_variants || []).some(v => v.name.toLowerCase().includes(search));
      if (!inOrig && !inVar) return false;
    }
    return true;
  });

  if (sortVal === 'name') {
    filtered.sort((a, b) => a.name_original.localeCompare(b.name_original));
  } else if (sortVal === 'year_start') {
    filtered.sort((a, b) => a.year_start - b.year_start);
  } else if (sortVal === 'confidence-desc') {
    filtered.sort((a, b) => b.confidence_score - a.confidence_score);
  }

  selectedCardIndex = -1;
  renderResults(filtered);
  renderMap(filtered);
}

// ─── Lista risultati ────────────────────────────────────────────

function renderResults(entities) {
  const el = document.getElementById('results-list');
  if (!entities.length) {
    el.innerHTML = `<p class="placeholder">${t('no_results')}</p>`;
    return;
  }

  const countInfo = `<div class="results-count">${entities.length} / ${allEntities.length} ${t('entities')}</div>`;

  el.innerHTML = countInfo + entities.map((e, idx) => {
    const pct = Math.round(e.confidence_score * 100);
    const real = isReal(e);
    const icon = TYPE_ICONS[e.entity_type] || '📍';
    return `
    <div class="result-card ${e.status}" data-id="${e.id}" data-idx="${idx}" role="listitem" tabindex="0">
      <div class="name"><span class="type-icon">${icon}</span> ${esc(e.name_original)}${real ? '' : ' <span class="precision-tag approx">~</span>'}</div>
      <div class="meta">
        ${e.entity_type} &middot;
        ${fmtY(e.year_start)}\u2013${e.year_end ? fmtY(e.year_end) : t('today')} &middot;
        <span class="status-badge ${e.status}">${t(e.status)}</span>
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
        m.bindTooltip(richTooltip(e), { direction: 'top' });
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
        layer.bindTooltip(richTooltip(e), { sticky: true });
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

function richTooltip(e) {
  const icon = TYPE_ICONS[e.entity_type] || '📍';
  const pct = Math.round(e.confidence_score * 100);
  const barColor = COLORS[e.status] || '#8b949e';
  return `
    <div style="min-width:160px">
      <strong>${icon} ${esc(e.name_original)}</strong><br>
      <span style="font-size:0.85em;opacity:0.8">${e.entity_type} &middot; ${fmtY(e.year_start)}\u2013${e.year_end ? fmtY(e.year_end) : t('today')}</span><br>
      <div style="display:flex;align-items:center;gap:6px;margin-top:3px">
        <div style="flex:1;height:3px;background:rgba(255,255,255,0.15);border-radius:2px">
          <div style="width:${pct}%;height:100%;background:${barColor};border-radius:2px"></div>
        </div>
        <span style="font-size:0.75em;opacity:0.7">${pct}%</span>
      </div>
      <span style="font-size:0.75em;opacity:0.6">${t(e.status)}</span>
    </div>`;
}

// ─── Dettaglio (con sezioni collassabili) ───────────────────────

async function showDetail(id) {
  const panel = document.getElementById('detail-panel');
  const content = document.getElementById('detail-content');
  panel.classList.remove('hidden');
  content.innerHTML = '<div class="detail-spinner"><div class="spinner"></div></div>';

  if (window.innerWidth <= 768) {
    document.getElementById('sidebar').classList.add('collapsed');
  }

  const info = document.getElementById('map-info');
  if (info) info.style.display = 'none';

  pushUrlState({ entity: id });

  const e = await loadDetail(id);
  if (!e) { panel.classList.add('hidden'); return; }

  const pct = Math.round(e.confidence_score * 100);
  const sc = COLORS[e.status] || '#8b949e';
  const real = isReal(e);
  const duration = e.year_end ? (e.year_end - e.year_start) : (new Date().getFullYear() - e.year_start);
  const cIcon = CONTINENT_ICONS[e.continent] || '🌐';

  // Boundary geometry summary
  let geoSummary = '';
  if (e.boundary_geojson) {
    const gt = e.boundary_geojson.type;
    if (gt === 'Point') {
      const [lon, lat] = e.boundary_geojson.coordinates;
      geoSummary = `<p class="geo-coords">📍 ${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E</p>`;
    } else if (gt === 'Polygon') {
      const pts = e.boundary_geojson.coordinates[0]?.length || 0;
      geoSummary = `<p class="geo-coords">🗺️ Polygon: ${pts} ${lang === 'it' ? 'vertici' : 'vertices'}</p>`;
    } else if (gt === 'MultiPolygon') {
      const polys = e.boundary_geojson.coordinates?.length || 0;
      geoSummary = `<p class="geo-coords">🗺️ MultiPolygon: ${polys} ${lang === 'it' ? 'regioni' : 'regions'}</p>`;
    }
  }

  let html = `
    <h2>${esc(e.name_original)}</h2>
    <div class="detail-tags">
      <span class="lang-tag">${e.name_original_lang}</span>
      <span class="status-badge ${e.status}">${t(e.status)}</span>
      <span class="continent-tag">${cIcon} ${e.continent || '?'}</span>
    </div>

    <div class="detail-section" data-section="info">
      <h3 class="collapsible" tabindex="0">${t('info')} <span class="collapse-icon">▾</span></h3>
      <div class="section-body">
        <div class="info-grid">
          <div class="info-item"><span class="info-label">${t('type') || 'Tipo'}</span><span class="info-value">${TYPE_ICONS[e.entity_type] || ''} ${e.entity_type}</span></div>
          <div class="info-item"><span class="info-label">${t('period')}</span><span class="info-value">${fmtY(e.year_start)} \u2013 ${e.year_end ? fmtY(e.year_end) : t('present')}</span></div>
          <div class="info-item"><span class="info-label">${t('duration') || 'Durata'}</span><span class="info-value">${duration.toLocaleString('it-IT')} ${t('years') || 'anni'}</span></div>
          ${e.capital ? `<div class="info-item"><span class="info-label">${t('capital')}</span><span class="info-value">${esc(e.capital.name)}${e.capital.lat ? ` <span class="geo-micro">(${e.capital.lat.toFixed(2)}°, ${e.capital.lon.toFixed(2)}°)</span>` : ''}</span></div>` : ''}
          <div class="info-item"><span class="info-label">${lang === 'it' ? 'Regione' : 'Region'}</span><span class="info-value">${cIcon} ${e.continent || '—'}</span></div>
        </div>
      </div>
    </div>

    <div class="detail-section" data-section="reliability">
      <h3 class="collapsible" tabindex="0">${t('reliability')} <span class="collapse-icon">▾</span></h3>
      <div class="section-body">
        <div class="confidence-bar"><div class="confidence-fill" style="width:${pct}%;background:${sc}"></div></div>
        <p style="font-size:0.78em;color:var(--text-muted);margin-top:4px">
          ${t('score')}: <strong>${e.confidence_score.toFixed(2)}</strong> / 1.00
          ${e.confidence_score < 0.6 ? ` \u2014 <span style="color:var(--uncertain)">${t('partial_data') || 'dati parziali'}</span>` : ''}
          ${e.confidence_score >= 0.85 ? ` \u2014 <span style="color:var(--confirmed)">\u2713 ${lang === 'it' ? 'alta affidabilit\u00e0' : 'high reliability'}</span>` : ''}
        </p>
        ${e.boundary_geojson ? (real ? `
          <div class="boundary-notice real-notice">
            \u2713 ${t('real_boundary')}
          </div>` : `
          <div class="boundary-notice">
            \u26a0 ${t('approx_boundary')}
          </div>`) : `
          <div class="boundary-notice" style="border-color:rgba(139,148,158,0.25);background:rgba(139,148,158,0.06);color:var(--text-muted)">
            ${lang === 'it' ? 'Nessun confine geografico disponibile' : 'No geographic boundary available'}
          </div>`}
        ${geoSummary}
      </div>
    </div>`;

  if (e.name_variants.length) {
    html += `
    <div class="detail-section" data-section="names">
      <h3 class="collapsible" tabindex="0">${t('names_section')} <span class="collapse-icon">▾</span></h3>
      <div class="section-body">
        <ul>${e.name_variants.map(v => `
          <li>
            <strong>${esc(v.name)}</strong> <span class="lang-tag">${v.lang}</span>
            ${v.period_start != null ? `<span style="font-size:0.75em;color:var(--text-muted)">${fmtY(v.period_start)}\u2013${v.period_end ? fmtY(v.period_end) : '...'}</span>` : ''}
            ${v.context ? `<br><span style="font-size:0.78em;color:var(--text-muted)">${esc(v.context)}</span>` : ''}
          </li>`).join('')}
        </ul>
      </div>
    </div>`;
  }

  if (e.territory_changes.length) {
    html += `
    <div class="detail-section" data-section="territory">
      <h3 class="collapsible" tabindex="0">${t('territory_section')} <span class="collapse-icon">▾</span></h3>
      <div class="section-body">
        <ul>${e.territory_changes.map(tc => `
          <li>
            <span class="change-type ${tc.change_type}">${tc.change_type.replace(/_/g, ' ')}</span>
            <strong>${fmtY(tc.year)}</strong> \u2014 ${esc(tc.region)}
            <span style="font-size:0.7em;color:var(--text-muted)">(${Math.round(tc.confidence_score*100)}%)</span>
            ${tc.description ? `<br><span style="font-size:0.8em">${esc(tc.description)}</span>` : ''}
            ${tc.population_affected ? `<br><span style="font-size:0.75em;color:var(--uncertain)">${t('pop_affected')}: ~${tc.population_affected.toLocaleString('it-IT')}</span>` : ''}
          </li>`).join('')}
        </ul>
      </div>
    </div>`;
  }

  if (e.sources.length) {
    const sourceIcons = { academic: '📚', primary: '📜', archaeological: '🏺', cartographic: '🗺️', official: '🏛️', modern_database: '💾', genetic: '🧬' };
    html += `
    <div class="detail-section" data-section="sources">
      <h3 class="collapsible" tabindex="0">${t('sources_section')} (${e.sources.length}) <span class="collapse-icon">▾</span></h3>
      <div class="section-body">
        <ul class="sources-list">${e.sources.map(s => `
          <li class="source-item">
            <span class="source-icon">${sourceIcons[s.source_type] || '📄'}</span>
            <div class="source-detail">
              <span class="source-citation">${esc(s.citation)}</span>
              <span class="source-type-tag">${s.source_type.replace(/_/g, ' ')}</span>
            </div>
          </li>`).join('')}
        </ul>
      </div>
    </div>`;
  }

  if (e.ethical_notes) {
    html += `
    <div class="detail-section" data-section="ethics">
      <h3 class="collapsible" tabindex="0">${t('ethics_section')} <span class="collapse-icon">▾</span></h3>
      <div class="section-body">
        <div class="ethics-box">${esc(e.ethical_notes)}</div>
      </div>
    </div>`;
  }

  // Contemporaries section
  html += `
    <div class="detail-section" data-section="contemporaries">
      <h3 class="collapsible" tabindex="0">${t('contemporaries') || 'Contemporanei'} <span class="collapse-icon">▾</span></h3>
      <div class="section-body" id="contemporaries-body">
        <div class="detail-spinner" style="height:60px"><div class="spinner" style="width:20px;height:20px"></div></div>
      </div>
    </div>`;

  // Action buttons
  html += `
    <div class="detail-actions">
      <button class="btn-share" onclick="shareEntity(${e.id})" title="${t('share') || 'Condividi'}">
        🔗 ${t('share') || 'Condividi'}
      </button>
      <button class="btn-compare" onclick="startCompare(${e.id})" title="Confronta con un'altra entit\u00e0">
        ⚖️ ${t('compare') || 'Confronta'}
      </button>
    </div>`;

  content.innerHTML = html;

  // Bind collapsible sections
  content.querySelectorAll('.collapsible').forEach(h3 => {
    h3.addEventListener('click', () => toggleSection(h3));
    h3.addEventListener('keydown', ev => { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); toggleSection(h3); } });
  });

  // Load contemporaries async
  loadContemporaries(id).then(data => {
    const body = document.getElementById('contemporaries-body');
    if (!body) return;
    if (!data || !data.contemporaries.length) {
      body.innerHTML = `<p style="font-size:0.8em;color:var(--text-muted)">${t('no_contemporaries') || 'Nessun contemporaneo trovato'}</p>`;
      return;
    }
    body.innerHTML = data.contemporaries.slice(0, 8).map(c => {
      const icon = TYPE_ICONS[c.entity_type] || '📍';
      return `<div class="contemporary-item" data-id="${c.id}" tabindex="0">
        <span class="type-icon">${icon}</span>
        <div>
          <strong>${esc(c.name_original)}</strong>
          <div style="font-size:0.72em;color:var(--text-muted)">${c.entity_type} &middot; ${fmtY(c.overlap_start)}\u2013${fmtY(c.overlap_end)}</div>
        </div>
      </div>`;
    }).join('');
    body.querySelectorAll('.contemporary-item').forEach(item => {
      const handler = () => showDetail(+item.dataset.id);
      item.addEventListener('click', handler);
      item.addEventListener('keydown', ev => { if (ev.key === 'Enter') handler(); });
    });
  });

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

function toggleSection(h3) {
  const section = h3.closest('.detail-section');
  section.classList.toggle('collapsed');
  const icon = h3.querySelector('.collapse-icon');
  if (icon) icon.textContent = section.classList.contains('collapsed') ? '▸' : '▾';
}

function shareEntity(id) {
  const url = `${window.location.origin}${window.location.pathname}?entity=${id}&year=${document.getElementById('year-slider').value}`;
  if (navigator.clipboard) {
    navigator.clipboard.writeText(url).then(() => {
      showToast(t('link_copied') || 'Link copiato!');
    });
  } else {
    prompt('Copia questo link:', url);
  }
}

function startCompare(id) {
  if (compareEntityId === null) {
    compareEntityId = id;
    showToast(t('compare_select') || 'Ora clicca su un\'altra entit\u00e0 per confrontarle');
    // Highlight cards with compare indicator
    document.querySelectorAll('.result-card').forEach(card => {
      if (+card.dataset.id !== id) {
        card.classList.add('compare-candidate');
        const origHandler = card.onclick;
        card.onclick = () => {
          showCompare(compareEntityId, +card.dataset.id);
          compareEntityId = null;
          document.querySelectorAll('.result-card').forEach(c => c.classList.remove('compare-candidate'));
        };
      }
    });
  } else {
    showCompare(compareEntityId, id);
    compareEntityId = null;
    document.querySelectorAll('.result-card').forEach(c => c.classList.remove('compare-candidate'));
  }
}

function showToast(msg) {
  const toast = document.getElementById('error-toast');
  const msgEl = document.getElementById('error-message');
  toast.style.background = 'rgba(63,185,80,0.95)';
  msgEl.textContent = msg;
  toast.classList.remove('hidden');
  setTimeout(() => { toast.classList.add('hidden'); toast.style.background = ''; }, 3000);
}

function closeDetail() {
  document.getElementById('detail-panel').classList.add('hidden');
  const info = document.getElementById('map-info');
  if (info) info.style.display = '';
  pushUrlState();
}

// ─── Error toast ────────────────────────────────────────────────

function showError(msg) {
  const toast = document.getElementById('error-toast');
  toast.style.background = '';
  document.getElementById('error-message').textContent = msg;
  toast.classList.remove('hidden');
  setTimeout(() => toast.classList.add('hidden'), 8000);
}

// ─── Events ─────────────────────────────────────────────────────

function bindEvents() {
  const searchInput = document.getElementById('search-input');
  const yearSlider = document.getElementById('year-slider');
  const yearDisplay = document.getElementById('year-display');
  const yearInput = document.getElementById('year-input');
  const yearEra = document.getElementById('year-era');

  document.getElementById('search-btn').addEventListener('click', () => { applyFilters(); pushUrlState(); });
  searchInput.addEventListener('keyup', e => { if (e.key === 'Enter') { applyFilters(); pushUrlState(); } });

  searchInput.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => { applyFilters(); pushUrlState(); }, 300);
  });

  yearSlider.addEventListener('input', () => {
    const val = +yearSlider.value;
    yearDisplay.textContent = fmtY(val);
    if (val < 0) {
      yearInput.value = Math.abs(val);
      yearEra.value = 'bc';
    } else {
      yearInput.value = val;
      yearEra.value = 'ad';
    }
  });
  yearSlider.addEventListener('change', () => { applyFilters(); pushUrlState(); });

  function applyYearInput() {
    let val = parseInt(yearInput.value, 10) || 0;
    if (yearEra.value === 'bc') val = -Math.abs(val);
    val = Math.max(-4500, Math.min(2025, val));
    yearSlider.value = val;
    yearDisplay.textContent = fmtY(val);
    applyFilters();
    pushUrlState();
  }

  document.getElementById('year-go').addEventListener('click', applyYearInput);
  yearInput.addEventListener('keyup', e => { if (e.key === 'Enter') applyYearInput(); });
  yearEra.addEventListener('change', applyYearInput);

  document.querySelectorAll('.year-presets button').forEach(btn => {
    btn.addEventListener('click', () => {
      const val = parseInt(btn.dataset.year, 10);
      yearSlider.value = val;
      yearDisplay.textContent = fmtY(val);
      if (val < 0) {
        yearInput.value = Math.abs(val);
        yearEra.value = 'bc';
      } else {
        yearInput.value = val;
        yearEra.value = 'ad';
      }
      applyFilters();
      pushUrlState();
    });
  });

  document.querySelectorAll('.checkbox-group input').forEach(cb => {
    cb.addEventListener('change', () => { applyFilters(); pushUrlState(); });
  });

  document.getElementById('sort-select').addEventListener('change', applyFilters);

  // Timeline toggle
  const tlToggle = document.getElementById('timeline-toggle');
  const tlCanvas = document.getElementById('timeline-canvas');
  if (tlToggle && tlCanvas) {
    tlToggle.addEventListener('click', () => {
      tlCanvas.classList.toggle('collapsed');
      tlToggle.textContent = tlCanvas.classList.contains('collapsed') ? 'Timeline \u25BC' : 'Timeline \u25B2';
      if (!tlCanvas.classList.contains('collapsed')) drawTimeline();
    });
  }

  yearSlider.addEventListener('input', () => { if (timelineData) drawTimeline(); });

  document.getElementById('reset-btn').addEventListener('click', () => {
    searchInput.value = '';
    yearSlider.value = 1500;
    yearDisplay.textContent = '1500';
    yearInput.value = 1500;
    yearEra.value = 'ad';
    document.querySelectorAll('.checkbox-group input').forEach(cb => { cb.checked = true; });
    document.getElementById('sort-select').value = '';
    activeType = '';
    activeContinent = '';
    document.querySelectorAll('#type-chips .chip').forEach(c => c.classList.remove('active'));
    const allChip = document.querySelector('#type-chips .chip[data-type=""]');
    if (allChip) allChip.classList.add('active');
    document.querySelectorAll('#continent-chips .chip').forEach(c => c.classList.remove('active'));
    const allContChip = document.querySelector('#continent-chips .chip[data-continent=""]');
    if (allContChip) allContChip.classList.add('active');
    applyFilters();
    closeDetail();
    pushUrlState();
  });

  document.getElementById('close-detail').addEventListener('click', closeDetail);
  document.getElementById('lang-toggle').addEventListener('click', switchLang);
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  initTheme();

  document.getElementById('map-fullscreen').addEventListener('click', () => {
    const container = document.getElementById('map-container');
    container.classList.toggle('fullscreen');
    setTimeout(() => map.invalidateSize(), 300);
  });

  document.getElementById('map-fit-all').addEventListener('click', () => {
    if (layerGroup.getLayers().length > 0) {
      const bounds = layerGroup.getBounds();
      if (bounds.isValid()) map.fitBounds(bounds, { padding: [30, 30] });
    }
  });

  document.getElementById('error-dismiss').addEventListener('click', () => {
    document.getElementById('error-toast').classList.add('hidden');
  });

  const toggle = document.getElementById('sidebar-toggle');
  const sidebar = document.getElementById('sidebar');
  if (toggle) {
    toggle.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
      toggle.setAttribute('aria-expanded', !sidebar.classList.contains('collapsed'));
    });
  }

  // Playback
  document.getElementById('play-btn').addEventListener('click', togglePlayback);

  // ─── Keyboard Navigation ──────────────────────────────────────
  document.addEventListener('keydown', handleKeyboard);
}

function handleKeyboard(e) {
  // Ignore if user is typing in input
  const tag = document.activeElement?.tagName;
  if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;

  switch (e.key) {
    case 'Escape': {
      const panel = document.getElementById('detail-panel');
      if (!panel.classList.contains('hidden')) {
        closeDetail();
        e.preventDefault();
      }
      break;
    }
    case 'ArrowDown': {
      e.preventDefault();
      navigateResults(1);
      break;
    }
    case 'ArrowUp': {
      e.preventDefault();
      navigateResults(-1);
      break;
    }
    case 'Enter': {
      const cards = document.querySelectorAll('.result-card');
      if (selectedCardIndex >= 0 && selectedCardIndex < cards.length) {
        showDetail(+cards[selectedCardIndex].dataset.id);
      }
      break;
    }
    case '/': {
      e.preventDefault();
      document.getElementById('search-input').focus();
      break;
    }
    case '?': {
      showKeyboardHelp();
      break;
    }
  }
}

function navigateResults(dir) {
  const cards = document.querySelectorAll('.result-card');
  if (!cards.length) return;

  cards.forEach(c => c.classList.remove('keyboard-focus'));
  selectedCardIndex += dir;
  if (selectedCardIndex < 0) selectedCardIndex = cards.length - 1;
  if (selectedCardIndex >= cards.length) selectedCardIndex = 0;

  const card = cards[selectedCardIndex];
  card.classList.add('keyboard-focus');
  card.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
}

function showKeyboardHelp() {
  const panel = document.getElementById('detail-panel');
  const content = document.getElementById('detail-content');
  panel.classList.remove('hidden');
  content.innerHTML = `
    <h2>Scorciatoie Tastiera</h2>
    <div class="detail-section">
      <div class="section-body">
        <table class="kbd-table">
          <tr><td><kbd>↑</kbd> <kbd>↓</kbd></td><td>Naviga risultati</td></tr>
          <tr><td><kbd>Enter</kbd></td><td>Apri entit\u00e0 selezionata</td></tr>
          <tr><td><kbd>Esc</kbd></td><td>Chiudi pannello</td></tr>
          <tr><td><kbd>/</kbd></td><td>Focus sulla ricerca</td></tr>
          <tr><td><kbd>?</kbd></td><td>Mostra aiuto</td></tr>
        </table>
      </div>
    </div>`;
}

// ─── Utility ────────────────────────────────────────────────────

function fmtY(y) {
  if (y < 0) return `${Math.abs(y)} ${t('bc')}`;
  return String(y);
}

function esc(s) {
  if (!s) return '';
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

// ─── Timeline ───────────────────────────────────────────────────

let timelineData = null;

async function loadTimeline() {
  try {
    const res = await fetch(`${API}/v1/export/timeline`);
    if (!res.ok) return;
    timelineData = await res.json();
    drawTimeline();
  } catch (_) {}
}

function drawTimeline() {
  if (!timelineData) return;
  const canvas = document.getElementById('timeline-chart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const rect = canvas.parentElement.getBoundingClientRect();
  canvas.width = rect.width * window.devicePixelRatio;
  canvas.height = 120 * window.devicePixelRatio;
  canvas.style.width = rect.width + 'px';
  ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

  const w = rect.width;
  const h = 120;
  const pad = { left: 40, right: 20, top: 10, bottom: 25 };
  const plotW = w - pad.left - pad.right;
  const plotH = h - pad.top - pad.bottom;

  ctx.clearRect(0, 0, w, h);

  const minY = timelineData.min_year;
  const maxY = Math.min(timelineData.max_year, 2025);
  const range = maxY - minY || 1;

  const yearToX = y => pad.left + ((y - minY) / range) * plotW;

  // Grid lines
  ctx.strokeStyle = 'rgba(48,54,61,0.5)';
  ctx.lineWidth = 0.5;
  const step = range > 2000 ? 500 : range > 500 ? 100 : 50;
  for (let y = Math.ceil(minY / step) * step; y <= maxY; y += step) {
    const x = yearToX(y);
    ctx.beginPath();
    ctx.moveTo(x, pad.top);
    ctx.lineTo(x, h - pad.bottom);
    ctx.stroke();
    ctx.fillStyle = '#8b949e';
    ctx.font = '9px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(y < 0 ? `${Math.abs(y)}aC` : String(y), x, h - 8);
  }

  const sorted = [...timelineData.items].sort((a, b) => {
    const durA = (a.end || 2025) - a.start;
    const durB = (b.end || 2025) - b.start;
    return durB - durA;
  });

  const barH = Math.min(8, plotH / sorted.length - 1);
  sorted.forEach((item, i) => {
    const x1 = yearToX(item.start);
    const x2 = yearToX(item.end || 2025);
    const y = pad.top + (i * (plotH / sorted.length));
    const color = COLORS[item.status] || '#8b949e';

    ctx.fillStyle = color;
    ctx.globalAlpha = 0.6;
    ctx.fillRect(x1, y, Math.max(x2 - x1, 2), barH);
    ctx.globalAlpha = 1;

    if (x2 - x1 > 50) {
      ctx.fillStyle = '#e6edf3';
      ctx.font = '8px sans-serif';
      ctx.textAlign = 'left';
      const label = item.name.length > 20 ? item.name.slice(0, 18) + '...' : item.name;
      ctx.fillText(label, x1 + 3, y + barH - 1);
    }
  });

  // Year indicator line
  const slider = document.getElementById('year-slider');
  if (slider) {
    const curYear = parseInt(slider.value, 10);
    const cx = yearToX(curYear);
    ctx.strokeStyle = '#e94560';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(cx, pad.top);
    ctx.lineTo(cx, h - pad.bottom);
    ctx.stroke();
  }

  // Make timeline clickable
  canvas.onclick = (e) => {
    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left);
    const clickedYear = Math.round(minY + ((x - pad.left) / plotW) * range);
    if (clickedYear >= minY && clickedYear <= maxY) {
      const slider = document.getElementById('year-slider');
      const yearInput = document.getElementById('year-input');
      const yearEra = document.getElementById('year-era');
      slider.value = clickedYear;
      document.getElementById('year-display').textContent = fmtY(clickedYear);
      if (clickedYear < 0) {
        yearInput.value = Math.abs(clickedYear);
        yearEra.value = 'bc';
      } else {
        yearInput.value = clickedYear;
        yearEra.value = 'ad';
      }
      applyFilters();
      pushUrlState();
      drawTimeline();
    }
  };

  canvas.style.cursor = 'crosshair';
}

// ─── i18n ───────────────────────────────────────────────────────

let lang = localStorage.getItem('atlaspi-lang') || 'it';

const I18N = {
  it: {
    search: 'Cerca per nome, anche varianti...',
    year: 'Anno', status: 'Status',
    confirmed: 'Confermato', uncertain: 'Incerto', disputed: 'Contestato',
    type: 'Tipo', sort_label: 'Ordina', sort_default: 'Predefinito',
    sort_name: 'Nome A-Z', sort_year: 'Anno', sort_conf: 'Affidabilit\u00e0',
    reset: 'Reset filtri', all: 'Tutti', loading: 'Caricamento...',
    no_results: 'Nessuna entit\u00e0 trovata', entities: 'entit\u00e0',
    sources: 'fonti', changes: 'cambi', contested: 'contestati',
    avg_conf: 'conf. media', info: 'Informazioni', reliability: 'Affidabilit\u00e0',
    names_section: 'Nomi e varianti (ETHICS-001)',
    territory_section: 'Cambiamenti territoriali (ETHICS-002)',
    sources_section: 'Fonti', ethics_section: 'Governance etica',
    period: 'Periodo', capital: 'Capitale', score: 'Score',
    today: 'oggi', present: 'presente', bc: 'a.C.',
    real_boundary: 'Confini da dataset accademici. Verificare le fonti per dettagli.',
    approx_boundary: 'Confini approssimativi a scopo dimostrativo.',
    pop_affected: 'Popolazione colpita',
    banner: 'Confini da fonti accademiche. Dati storici da Natural Earth e aourednik/historical-basemaps.',
    map_hint: "Seleziona un'entit\u00e0 dalla lista o clicca su un'area della mappa.",
    share: 'Condividi', link_copied: 'Link copiato negli appunti!',
    partial_data: 'dati parziali o incerti',
    contemporaries: 'Contemporanei',
    no_contemporaries: 'Nessun contemporaneo trovato',
    error_connection: 'Impossibile caricare i dati. Verifica che il server sia attivo.',
    error_detail: 'Errore nel caricamento dei dettagli.',
    keyboard_help: 'Scorciatoie tastiera',
    compare: 'Confronta',
    compare_select: "Ora clicca su un'altra entit\u00e0 per confrontarle",
    duration: 'Durata',
    temporal_overlap: 'Sovrapposizione temporale',
    years: 'anni',
    no_overlap: 'Nessuna sovrapposizione',
    view: 'Vedi',
  },
  en: {
    search: 'Search by name, including variants...',
    year: 'Year', status: 'Status',
    confirmed: 'Confirmed', uncertain: 'Uncertain', disputed: 'Disputed',
    type: 'Type', sort_label: 'Sort', sort_default: 'Default',
    sort_name: 'Name A-Z', sort_year: 'Year', sort_conf: 'Reliability',
    reset: 'Reset filters', all: 'All', loading: 'Loading...',
    no_results: 'No entities found', entities: 'entities',
    sources: 'sources', changes: 'changes', contested: 'contested',
    avg_conf: 'avg conf.', info: 'Information', reliability: 'Reliability',
    names_section: 'Names & variants (ETHICS-001)',
    territory_section: 'Territory changes (ETHICS-002)',
    sources_section: 'Sources', ethics_section: 'Ethical governance',
    period: 'Period', capital: 'Capital', score: 'Score',
    today: 'today', present: 'present', bc: 'BC',
    real_boundary: 'Boundaries from academic datasets. Check sources for details.',
    approx_boundary: 'Approximate boundaries for demonstration.',
    pop_affected: 'Population affected',
    banner: 'Boundaries from academic sources. Data from Natural Earth and aourednik/historical-basemaps.',
    map_hint: 'Select an entity from the list or click on the map.',
    share: 'Share', link_copied: 'Link copied to clipboard!',
    partial_data: 'partial or uncertain data',
    contemporaries: 'Contemporaries',
    no_contemporaries: 'No contemporaries found',
    error_connection: 'Unable to load data. Check if the server is running.',
    error_detail: 'Error loading details.',
    keyboard_help: 'Keyboard shortcuts',
    compare: 'Compare',
    compare_select: 'Now click another entity to compare them',
    duration: 'Duration',
    temporal_overlap: 'Temporal overlap',
    years: 'years',
    no_overlap: 'No overlap',
    view: 'View',
  },
};

function t(key) { return (I18N[lang] || I18N.it)[key] || key; }

function initLang() {
  document.getElementById('lang-toggle').textContent = lang === 'it' ? 'EN' : 'IT';
  applyLangUI();
}

function switchLang() {
  lang = lang === 'it' ? 'en' : 'it';
  localStorage.setItem('atlaspi-lang', lang);
  document.getElementById('lang-toggle').textContent = lang === 'it' ? 'EN' : 'IT';
  applyLangUI();
  pushUrlState();
}

function applyLangUI() {
  document.getElementById('search-input').placeholder = t('search');
  document.getElementById('reset-btn').textContent = t('reset');
  const banner = document.querySelector('.data-banner');
  if (banner) banner.innerHTML = `<strong>${t('banner').split('.')[0]}.</strong> ${t('banner').split('.').slice(1).join('.')}`;
  const info = document.getElementById('map-info');
  if (info) info.textContent = t('map_hint');
  applyFilters();
  loadStats();
}

// ─── Playback ───────────────────────────────────────────────────

function togglePlayback() {
  const btn = document.getElementById('play-btn');
  if (playbackInterval) {
    clearInterval(playbackInterval);
    playbackInterval = null;
    btn.textContent = '▶';
    btn.classList.remove('playing');
    return;
  }

  btn.textContent = '⏸';
  btn.classList.add('playing');

  const speed = parseInt(document.getElementById('play-speed').value, 10);
  const slider = document.getElementById('year-slider');
  const yearInput = document.getElementById('year-input');
  const yearEra = document.getElementById('year-era');
  const yearDisplay = document.getElementById('year-display');

  // Step size depends on the range
  const currentYear = parseInt(slider.value, 10);
  const step = currentYear < -1000 ? 100 : currentYear < 0 ? 50 : currentYear < 1000 ? 25 : 10;

  playbackInterval = setInterval(() => {
    let val = parseInt(slider.value, 10) + step;
    if (val > 2025) {
      val = -4500; // Loop back
    }

    slider.value = val;
    yearDisplay.textContent = fmtY(val);
    if (val < 0) {
      yearInput.value = Math.abs(val);
      yearEra.value = 'bc';
    } else {
      yearInput.value = val;
      yearEra.value = 'ad';
    }
    applyFilters();
    if (timelineData) drawTimeline();
  }, speed);
}

// ─── Compare ────────────────────────────────────────────────────

async function showCompare(id1, id2) {
  const panel = document.getElementById('detail-panel');
  const content = document.getElementById('detail-content');
  panel.classList.remove('hidden');
  content.innerHTML = '<div class="detail-spinner"><div class="spinner"></div></div>';

  try {
    const res = await fetch(`${API}/v1/compare/${id1}/${id2}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const a = data.entity_a;
    const b = data.entity_b;
    const cmp = data.comparison;

    content.innerHTML = `
      <h2>Confronto</h2>
      <div class="compare-panel">
        <div class="compare-card" style="border-top:3px solid ${COLORS[a.status]}">
          <h4>${TYPE_ICONS[a.entity_type] || ''} ${esc(a.name_original)}</h4>
          <div class="compare-stat"><span class="label">${t('type')}</span><span class="value">${a.entity_type}</span></div>
          <div class="compare-stat"><span class="label">${t('period')}</span><span class="value">${fmtY(a.year_start)}–${a.year_end ? fmtY(a.year_end) : t('present')}</span></div>
          <div class="compare-stat"><span class="label">Durata</span><span class="value">${a.duration_years} anni</span></div>
          <div class="compare-stat"><span class="label">${t('score')}</span><span class="value">${Math.round(a.confidence_score*100)}%</span></div>
          <div class="compare-stat"><span class="label">Status</span><span class="value"><span class="status-badge ${a.status}">${t(a.status)}</span></span></div>
          <div class="compare-stat"><span class="label">${t('sources')}</span><span class="value">${a.sources_count}</span></div>
          <div class="compare-stat"><span class="label">${t('changes')}</span><span class="value">${a.territory_changes_count}</span></div>
          ${a.capital ? `<div class="compare-stat"><span class="label">${t('capital')}</span><span class="value">${esc(a.capital.name)}</span></div>` : ''}
        </div>
        <div class="compare-card" style="border-top:3px solid ${COLORS[b.status]}">
          <h4>${TYPE_ICONS[b.entity_type] || ''} ${esc(b.name_original)}</h4>
          <div class="compare-stat"><span class="label">${t('type')}</span><span class="value">${b.entity_type}</span></div>
          <div class="compare-stat"><span class="label">${t('period')}</span><span class="value">${fmtY(b.year_start)}–${b.year_end ? fmtY(b.year_end) : t('present')}</span></div>
          <div class="compare-stat"><span class="label">Durata</span><span class="value">${b.duration_years} anni</span></div>
          <div class="compare-stat"><span class="label">${t('score')}</span><span class="value">${Math.round(b.confidence_score*100)}%</span></div>
          <div class="compare-stat"><span class="label">Status</span><span class="value"><span class="status-badge ${b.status}">${t(b.status)}</span></span></div>
          <div class="compare-stat"><span class="label">${t('sources')}</span><span class="value">${b.sources_count}</span></div>
          <div class="compare-stat"><span class="label">${t('changes')}</span><span class="value">${b.territory_changes_count}</span></div>
          ${b.capital ? `<div class="compare-stat"><span class="label">${t('capital')}</span><span class="value">${esc(b.capital.name)}</span></div>` : ''}
        </div>
      </div>
      <div class="compare-overlap">
        <div style="font-size:0.78em;color:var(--text-muted);margin-bottom:4px">Sovrapposizione temporale</div>
        <div class="overlap-value">${cmp.temporal_overlap_years} anni</div>
        ${cmp.overlap_period ? `<div style="font-size:0.75em;color:var(--text-muted);margin-top:2px">${cmp.overlap_period}</div>` : '<div style="font-size:0.75em;color:var(--text-muted)">Nessuna sovrapposizione</div>'}
      </div>
      <div class="detail-actions">
        <button class="btn-share" onclick="showDetail(${a.id})">Vedi ${esc(a.name_original)}</button>
        <button class="btn-share" onclick="showDetail(${b.id})">Vedi ${esc(b.name_original)}</button>
      </div>`;

    // Fit both on map
    if (a.boundary_geojson && b.boundary_geojson) {
      try {
        const la = L.geoJSON(a.boundary_geojson);
        const lb = L.geoJSON(b.boundary_geojson);
        const bounds = la.getBounds().extend(lb.getBounds());
        map.fitBounds(bounds, { padding: [50, 50] });
      } catch (_) {}
    }
  } catch (err) {
    content.innerHTML = '<p class="placeholder">Errore nel confronto</p>';
  }
}

// ─── Theme ─────────────────────────────────────────────────────

function initTheme() {
  const saved = localStorage.getItem('atlaspi-theme') || 'dark';
  applyTheme(saved);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'dark';
  const next = current === 'dark' ? 'light' : 'dark';
  applyTheme(next);
  localStorage.setItem('atlaspi-theme', next);
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  const btn = document.getElementById('theme-toggle');
  if (btn) btn.textContent = theme === 'dark' ? '☀️' : '🌙';
  // Invalidate map size after theme change
  setTimeout(() => { if (map) map.invalidateSize(); }, 100);
}

function isReal(e) {
  if (!e.boundary_geojson) return false;
  const g = e.boundary_geojson;
  let pts = 0;
  if (g.type === 'Polygon') pts = g.coordinates.reduce((s, r) => s + r.length, 0);
  else if (g.type === 'MultiPolygon') pts = g.coordinates.reduce((s, p) => s + p.reduce((s2, r) => s2 + r.length, 0), 0);
  return pts > 50;
}
