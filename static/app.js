/* AtlasPI v6.23.0 — Events overlay on map, trade routes, dynasty chains, unified timeline */

const API = '';
const COLORS = {
  confirmed: '#3fb950',
  uncertain: '#d29922',
  disputed: '#f85149',
};

// Trade route styling (Feature 1)
const ROUTE_STYLES = {
  maritime: { color: '#2188ff', weight: 2, opacity: 0.6, dashArray: '6,4' },
  overland: { color: '#8b4513', weight: 2, opacity: 0.6, dashArray: null },
  river:    { color: '#00bcd4', weight: 2, opacity: 0.6, dashArray: null },
  mixed:    { color: '#8b5cf6', weight: 2, opacity: 0.6, dashArray: '6,4' },
};
const SLAVERY_OUTLINE = { color: '#dc2626', weight: 4, opacity: 0.4, dashArray: null };

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
let acDebounceTimer = null;
let activeType = '';
let activeContinent = '';
let selectedCardIndex = -1;
let acSelectedIndex = -1;
let playbackInterval = null;
let compareEntityId = null;

// v6.7 — Trade routes overlay state
let tradeRoutesLayer = null;   // Leaflet layerGroup for routes
let tradeRoutesData = null;    // Cached raw routes list
let tradeRoutesEnabled = false;

// v6.23 — Events overlay state
let eventsOverlayLayer = null;   // Leaflet layerGroup for event markers
let eventsOverlayEnabled = false;
let eventsOverlayCache = {};     // keyed by year

// v6.7 — Chains sidebar state
let chainsData = null;         // Cached chain index
let chainDetailCache = {};     // Full chain details keyed by id

// v6.7 — Current entity being viewed in detail panel (for tab switching)
let currentDetailEntity = null;
let currentDetailTab = 'overview'; // 'overview' | 'timeline'

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
  // v6.64: initLang first so applyFilters in loadEntities uses correct language
  // labels. Avoids URL race where ?year=X loads with 0 entities (report #03).
  initLang();
  loadTypes();
  loadContinents();
  loadStats();
  loadTimeline();
  loadChains();
  bindEvents();
  // v6.66 FIX 1: inietta i numeri live per onboarding + footer + qualunque
  // elemento con [data-i18n] che contiene placeholder {entities} {events}...
  // Single source of truth: /health + /v1/* endpoints. Nessun valore statico.
  hydrateLiveStats();
  loadEntities().then(() => {
    restoreUrlState();
    // v6.64: force a final applyFilters after restoreUrlState, regardless
    // of whether URL params triggered `changed`. Ensures entities render
    // even when the URL has no filter params.
    applyFilters();
  });
});

// v6.66 FIX 1: fetch dinamico dei conteggi. Popola i18nVars con i numeri
// reali così le stringhe tradotte con {entities}/{events}/{rulers}/{sites}
// vengono interpolate con i valori correnti. Tutto fire-and-forget.
function hydrateLiveStats() {
  if (!('fetch' in window) || typeof window.setI18nStats !== 'function') return;
  const stats = {};
  const fmt = (n) => (typeof n === 'number' ? n.toLocaleString() : String(n));
  const pick = (j) => {
    if (!j) return null;
    if (typeof j.count === 'number') return j.count;
    if (typeof j.total === 'number') return j.total;
    if (typeof j.entity_count === 'number') return j.entity_count;
    return null;
  };
  const calls = [
    ['entities', '/v1/entities?limit=1'],
    ['events',   '/v1/events?limit=1'],
    ['rulers',   '/v1/rulers?limit=1'],
    ['sites',    '/v1/sites?limit=1'],
    ['periods',  '/v1/periods?limit=1'],
    ['chains',   '/v1/chains?limit=1'],
    ['cities',   '/v1/cities?limit=1'],
    ['languages', '/v1/languages?limit=1'],
  ];
  // Promise.allSettled così una singola API fallita non blocca le altre
  Promise.allSettled(calls.map(([k, url]) =>
    fetch(url, { cache: 'no-store' })
      .then(r => r.ok ? r.json() : null)
      .then(j => {
        const n = pick(j);
        if (n !== null) stats[k] = fmt(n);
      })
  )).then(() => {
    if (Object.keys(stats).length) window.setI18nStats(stats);
  });

  // Version injection nel footer: /health → span#footer-version
  fetch('/health', { cache: 'no-store' })
    .then(r => r.ok ? r.json() : null)
    .then(h => {
      if (!h) return;
      const vEl = document.getElementById('footer-version');
      if (vEl && h.version) vEl.textContent = h.version;
    })
    .catch(() => {});
}

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
  // v6.23 — Events overlay lives above entities but below trade routes
  eventsOverlayLayer = L.layerGroup();
  // Trade routes live in a dedicated layer sitting above entities (Feature 1)
  tradeRoutesLayer = L.layerGroup();

  // Right-click on map → find nearby entities
  map.on('contextmenu', async (e) => {
    e.originalEvent.preventDefault();
    const { lat, lng } = e.latlng;
    const year = parseInt(document.getElementById('year-slider').value, 10);
    try {
      const res = await fetch(`${API}/v1/nearby?lat=${lat.toFixed(4)}&lon=${lng.toFixed(4)}&year=${year}&radius=1000&limit=8`);
      if (!res.ok) return;
      const data = await res.json();
      if (!data.entities.length) {
        L.popup().setLatLng(e.latlng)
          .setContent(`<div style="font-size:0.85em;color:#8b949e">${t('no_results')}</div>`)
          .openOn(map);
        return;
      }
      const html = `<div style="min-width:200px;max-height:250px;overflow-y:auto">
        <div style="font-weight:600;margin-bottom:6px;font-size:0.85em">${t('nearby')} (${fmtY(year)})</div>
        ${data.entities.map(ne => {
          const icon = TYPE_ICONS[ne.entity_type] || '\ud83d\udccd';
          return `<div class="nearby-popup-item" data-id="${ne.id}" style="padding:4px 0;border-bottom:1px solid rgba(255,255,255,0.1);cursor:pointer;font-size:0.82em">
            ${icon} <strong>${esc(ne.name_original)}</strong>
            <span style="color:#8b949e;font-size:0.85em">${ne.distance_km} km</span>
          </div>`;
        }).join('')}
      </div>`;
      const popup = L.popup({ maxWidth: 280 }).setLatLng(e.latlng).setContent(html).openOn(map);
      setTimeout(() => {
        document.querySelectorAll('.nearby-popup-item').forEach(item => {
          item.addEventListener('click', () => { map.closePopup(); showDetail(+item.dataset.id); });
        });
      }, 50);
    } catch (_) {}
  });
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
  // v6.68: first-paint ottimizzato via /v1/entities/light.
  //
  // Strategia progressive:
  //   1) Phase 1 (fast): /v1/entities/light scarica 1034 entità in ~500ms
  //      con metadata (id, name, year, capital, type, continent, confidence,
  //      status) ma SENZA boundary_geojson. Permette first render immediato:
  //      entity count, search, filtri, timeline, list results funzionano
  //      subito. Capital markers renderizzabili.
  //   2) Phase 2 (background): paginata /v1/entities?limit=100 riempie
  //      progressivamente `boundary_geojson` nelle entità già presenti.
  //      Ogni pagina arriva → re-render mappa polygon per quelle entità.
  //
  // Prima di v6.68 l'utente aspettava 15s prima di vedere qualcosa.
  // Ora search/filter/list sono operativi entro ~500ms, mappa polygon
  // si completa progressivamente in background.
  const loadBar = document.getElementById('loading-bar');
  try {
    allEntities = [];
    if (loadBar) { loadBar.style.width = '5%'; loadBar.style.opacity = '1'; }

    // ─── Phase 1: fast metadata load via /v1/entities/light ──────
    const lightRes = await fetch(`${API}/v1/entities/light?limit=2000`, { cache: 'no-cache' });
    if (!lightRes.ok) throw new Error(`HTTP ${lightRes.status}`);
    const lightData = await lightRes.json();
    allEntities = (lightData.entities || []).map(e => ({ ...e, _has_boundary: false }));
    if (loadBar) loadBar.style.width = '40%';
    document.getElementById('entity-count').textContent = `${allEntities.length} ${t('entities')}`;
    applyFilters(); // first render: markers + search + filters operativi

    // ─── Phase 2: progressive boundary load in background ──────
    // Non bloccante: ritorna subito, il caricamento avviene in background.
    loadEntityBoundariesInBackground(loadBar);
  } catch (err) {
    if (loadBar) { loadBar.style.width = '100%'; loadBar.style.background = 'var(--disputed)'; }
    showError(t('error_connection') || 'Impossibile caricare i dati.');
    document.getElementById('results-list').innerHTML =
      '<p class="placeholder">Errore di connessione</p>';
  }
}

async function loadEntityBoundariesInBackground(loadBar) {
  // v6.68: carica progressivamente boundary_geojson via /v1/entities paginato.
  // Merge in place in allEntities (che contiene già metadata via light).
  const byId = new Map();
  allEntities.forEach(e => byId.set(e.id, e));

  let offset = 0;
  const limit = 100;
  let total = Infinity;

  while (offset < total) {
    try {
      const res = await fetch(`${API}/v1/entities?limit=${limit}&offset=${offset}`, { cache: 'no-cache' });
      if (!res.ok) break;
      const data = await res.json();
      total = data.total ?? data.count ?? 0;
      const batch = data.entities || [];
      if (batch.length === 0) break;

      batch.forEach(full => {
        const existing = byId.get(full.id);
        if (existing) {
          existing.boundary_geojson = full.boundary_geojson;
          existing.name_variants = full.name_variants;
          existing.sources = full.sources;
          existing.ethical_notes = full.ethical_notes;
          existing.territory_changes = full.territory_changes;
          existing._has_boundary = true;
        } else {
          // edge case: entità presente in /v1/entities ma non in /light
          const withFlag = { ...full, _has_boundary: true };
          byId.set(full.id, withFlag);
          allEntities.push(withFlag);
        }
      });

      offset += limit;
      if (loadBar && total > 0) {
        const pct = 40 + Math.round((offset / total) * 55);
        loadBar.style.width = `${Math.min(95, pct)}%`;
      }

      // Re-render mappa incrementale: ogni ~200 entità o a fine batch
      if (offset % 200 === 0 || offset >= total) {
        applyFilters();
      }
    } catch (e) {
      // Network error: interrompi senza mostrare errore bloccante
      break;
    }
  }

  if (loadBar) {
    loadBar.style.width = '100%';
    setTimeout(() => { loadBar.style.opacity = '0'; }, 300);
  }
  applyFilters(); // final render with all boundaries
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

async function loadSnapshotSummary(year) {
  try {
    const res = await fetch(`${API}/v1/snapshot/${year}`, { cache: 'no-cache' });
    if (!res.ok) return;
    const s = await res.json();
    const bar = document.getElementById('stats-bar');
    const topTypes = Object.entries(s.summary.types)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([k, v]) => `${TYPE_ICONS[k] || ''} ${v}`)
      .join(' ');
    bar.innerHTML = `
      <span class="stat-item"><span class="stat-value">${s.count}</span> ${t('active_in')} ${fmtY(year)}</span>
      <span class="stat-item">${topTypes}</span>
    `;
  } catch (_) {}
}

// ─── Trade Routes overlay (v6.7, Feature 1) ────────────────────

// ETHICS-010: slavery routes get a thicker red outline layered beneath
// the normal line to signal the human cost without sensationalizing —
// the visual cue is a hint that the route has `ethical_notes`, which
// the user must actively open to read.
async function loadTradeRoutes() {
  if (tradeRoutesData) return tradeRoutesData;
  try {
    // v6.34: fix — backend expone /v1/routes (vedi src/api/routes/cities_routes.py)
    const res = await fetch(`${API}/v1/routes`, { cache: 'no-cache' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    // Response may be { routes: [...] } or a bare array
    tradeRoutesData = Array.isArray(data) ? data : (data.routes || data.items || []);
    return tradeRoutesData;
  } catch (err) {
    showError(lang === 'it' ? 'Impossibile caricare le rotte commerciali.' : 'Unable to load trade routes.');
    return [];
  }
}

function extractRouteCoords(route) {
  // v6.68: allineato al contratto backend v6.66+ (list endpoint expone
  // geometry_simplified + start_lat/lon + end_lat/lon direttamente).
  // Ordine di preferenza:
  //   1) geometry_simplified: GeoJSON LineString ({type, coordinates: [[lon,lat],...]})
  //   2) start_lat/start_lon + end_lat/end_lon (fallback a 2 punti)
  //   3) legacy fields start/waypoints/end/path (backward compat)
  const pts = [];
  const pushPoint = (p) => {
    if (!p) return;
    if (Array.isArray(p) && p.length >= 2 && typeof p[0] === 'number') {
      // GeoJSON-style [lon, lat]
      pts.push([p[1], p[0]]);
      return;
    }
    if (typeof p === 'object') {
      const lat = p.lat ?? p.latitude;
      const lon = p.lon ?? p.lng ?? p.longitude;
      if (typeof lat === 'number' && typeof lon === 'number') pts.push([lat, lon]);
    }
  };

  // 1) geometry_simplified (preferito — più di 2 punti, utile per rotte curve)
  if (route.geometry_simplified && Array.isArray(route.geometry_simplified.coordinates)) {
    route.geometry_simplified.coordinates.forEach(p => pushPoint(p));
    if (pts.length >= 2) return pts;
  }

  // 2) start_lat/start_lon + end_lat/end_lon (contratto v6.66+ list endpoint)
  if (typeof route.start_lat === 'number' && typeof route.start_lon === 'number') {
    pts.push([route.start_lat, route.start_lon]);
  }
  if (typeof route.end_lat === 'number' && typeof route.end_lon === 'number') {
    pts.push([route.end_lat, route.end_lon]);
  }
  if (pts.length >= 2) return pts;

  // 3) Legacy fallback (detail endpoint o backend pre-v6.66)
  pushPoint(route.start || route.start_point || route.origin);
  const waypoints = route.waypoints || route.intermediate_points || [];
  if (Array.isArray(waypoints)) waypoints.forEach(pushPoint);
  pushPoint(route.end || route.end_point || route.destination);

  if (!pts.length && Array.isArray(route.path)) {
    route.path.forEach(p => pushPoint(p));
  }
  return pts;
}

function routeActiveInYear(route, year) {
  // v6.68: allineato a contratto backend (start_year/end_year). Mantiene
  // fallback a active_period_start/end per backward compat.
  const s = route.start_year ?? route.active_period_start;
  const e = route.end_year ?? route.active_period_end;
  if (typeof s === 'number' && s > year) return false;
  if (typeof e === 'number' && e < year) return false;
  return true;
}

function renderTradeRoutes() {
  if (!tradeRoutesLayer) return;
  tradeRoutesLayer.clearLayers();
  if (!tradeRoutesEnabled || !tradeRoutesData) return;

  const year = parseInt(document.getElementById('year-slider').value, 10);
  let rendered = 0;

  tradeRoutesData.forEach(route => {
    if (!routeActiveInYear(route, year)) return;
    const coords = extractRouteCoords(route);
    if (coords.length < 2) return;

    const type = (route.route_type || route.type || 'overland').toLowerCase();
    const style = ROUTE_STYLES[type] || ROUTE_STYLES.overland;

    // ETHICS-010: slavery outline rendered first so it sits beneath
    if (route.involves_slavery) {
      const outline = L.polyline(coords, {
        color: SLAVERY_OUTLINE.color,
        weight: SLAVERY_OUTLINE.weight,
        opacity: SLAVERY_OUTLINE.opacity,
        interactive: false,
        className: 'trade-route-slavery-outline',
      });
      outline.bindTooltip(
        lang === 'it'
          ? 'Rotta associata alla tratta schiavistica — vedi ETHICS-010'
          : 'Route linked to slave trade — see ETHICS-010',
        { sticky: true, direction: 'top' }
      );
      tradeRoutesLayer.addLayer(outline);
    }

    const line = L.polyline(coords, {
      color: style.color,
      weight: style.weight,
      opacity: style.opacity,
      dashArray: style.dashArray,
      className: `trade-route trade-route-${type}${route.involves_slavery ? ' trade-route-slavery' : ''}`,
    });

    line.bindTooltip(tradeRouteTooltip(route), { sticky: true, direction: 'top' });
    line.on('click', (ev) => {
      // Open detailed popup at click point
      L.popup({ maxWidth: 320, className: 'trade-route-popup' })
        .setLatLng(ev.latlng)
        .setContent(tradeRoutePopup(route))
        .openOn(map);
    });

    tradeRoutesLayer.addLayer(line);
    rendered += 1;
  });

  // Ensure the layer is attached to the map
  if (!map.hasLayer(tradeRoutesLayer)) tradeRoutesLayer.addTo(map);
  return rendered;
}

function tradeRouteTooltip(route) {
  // v6.68: allineato a contratto backend (name_original, start_year/end_year, commodities)
  const name = esc(route.name_original || route.name || (lang === 'it' ? 'Rotta senza nome' : 'Unnamed route'));
  const s = route.start_year ?? route.active_period_start;
  const e = route.end_year ?? route.active_period_end;
  const period = (s != null || e != null)
    ? `${s != null ? fmtY(s) : '?'}–${e != null ? fmtY(e) : (lang === 'it' ? 'oggi' : 'today')}`
    : '';
  const rawCommodities = route.commodities ?? route.commodities_primary;
  const commodities = Array.isArray(rawCommodities)
    ? rawCommodities.slice(0, 4).map(esc).join(', ')
    : (rawCommodities ? esc(String(rawCommodities)) : '');

  return `
    <div style="min-width:180px">
      <strong>${name}</strong>${route.involves_slavery ? ' <span style="color:#dc2626;font-size:0.82em">&#x26A0; ETHICS-010</span>' : ''}<br>
      ${period ? `<span style="font-size:0.82em;opacity:0.85">${period}</span><br>` : ''}
      ${commodities ? `<span style="font-size:0.78em;opacity:0.75">${commodities}</span>` : ''}
    </div>`;
}

function tradeRoutePopup(route) {
  // v6.68: allineato a contratto backend
  const name = esc(route.name_original || route.name || (lang === 'it' ? 'Rotta senza nome' : 'Unnamed route'));
  const type = (route.route_type || route.type || '—');
  const s = route.start_year ?? route.active_period_start;
  const e = route.end_year ?? route.active_period_end;
  const period = `${s != null ? fmtY(s) : '?'} – ${e != null ? fmtY(e) : (lang === 'it' ? 'oggi' : 'today')}`;
  const rawCommodities = route.commodities ?? route.commodities_primary;
  const commodities = Array.isArray(rawCommodities)
    ? rawCommodities.map(esc).join(', ')
    : (rawCommodities ? esc(String(rawCommodities)) : '—');
  const notes = route.ethical_notes ? esc(route.ethical_notes) : '';
  const conf = (typeof route.confidence_score === 'number')
    ? ` · ${Math.round(route.confidence_score * 100)}%` : '';

  return `
    <div class="trade-route-popup-body">
      <div class="tr-popup-title"><strong>${name}</strong>${route.involves_slavery ? ' <span class="tr-slavery-tag">ETHICS-010</span>' : ''}</div>
      <div class="tr-popup-meta">
        <span class="tr-popup-type tr-type-${type}">${esc(type)}</span>
        <span>${period}${conf}</span>
      </div>
      <div class="tr-popup-row"><span>${lang === 'it' ? 'Merci' : 'Commodities'}:</span> ${commodities}</div>
      ${route.involves_slavery ? `
        <div class="tr-ethics-box">
          <strong>${lang === 'it' ? 'Nota etica (ETHICS-010)' : 'Ethical note (ETHICS-010)'}:</strong>
          ${notes || (lang === 'it'
            ? 'Questa rotta &egrave; stata associata alla tratta schiavistica. La sua rappresentazione serve a documentare, non a celebrare.'
            : 'This route was associated with the slave trade. It is documented, not celebrated.')}
        </div>` : (notes ? `<div class="tr-ethics-box tr-ethics-neutral">${notes}</div>` : '')}
    </div>`;
}

function toggleTradeRoutes(enabled) {
  tradeRoutesEnabled = !!enabled;
  const legend = document.getElementById('trade-routes-legend');
  if (legend) legend.classList.toggle('hidden', !tradeRoutesEnabled);

  if (!tradeRoutesEnabled) {
    if (tradeRoutesLayer) tradeRoutesLayer.clearLayers();
    return;
  }

  // Lazy-load on first activation
  loadTradeRoutes().then(() => renderTradeRoutes());
}

// ─── Events Overlay on Map (v6.23) ──────────────────────────────

const EVENT_TYPE_ICONS = {
  BATTLE: '⚔️', SIEGE: '🏰', TREATY: '📜', REBELLION: '🔥',
  REVOLUTION: '✊', CORONATION: '👑', DEATH_OF_RULER: '💀',
  MARRIAGE_DYNASTIC: '💍', FOUNDING_CITY: '🏙️', FOUNDING_STATE: '🏛️',
  DISSOLUTION_STATE: '💔', CONQUEST: '🗡️', COLONIAL_VIOLENCE: '⛓️',
  GENOCIDE: '☠️', ETHNIC_CLEANSING: '⚠️', MASSACRE: '🩸',
  DEPORTATION: '🚶', FAMINE: '🌾', EPIDEMIC: '🦠',
  EARTHQUAKE: '🌍', VOLCANIC_ERUPTION: '🌋', TSUNAMI: '🌊',
  FLOOD: '💧', DROUGHT: '☀️', FIRE: '🔥',
  MIGRATION: '🚶‍♂️', COLLAPSE: '📉',
  EXPLORATION: '🧭', TRADE_AGREEMENT: '🤝', RELIGIOUS_EVENT: '⛪',
  INTELLECTUAL_EVENT: '📖', TECHNOLOGICAL_EVENT: '⚙️', OTHER: '📌',
};

function eventTypeClass(eventType) {
  if (!eventType) return 'ev-other';
  const t = eventType.toUpperCase();
  if (['BATTLE', 'SIEGE', 'REBELLION', 'REVOLUTION', 'COLLAPSE'].includes(t)) return 'ev-battle';
  if (['TREATY', 'TRADE_AGREEMENT', 'MARRIAGE_DYNASTIC', 'CORONATION'].includes(t)) return 'ev-treaty';
  if (['FOUNDING_CITY', 'FOUNDING_STATE', 'EXPLORATION'].includes(t)) return 'ev-founding';
  if (['GENOCIDE', 'ETHNIC_CLEANSING', 'MASSACRE', 'COLONIAL_VIOLENCE', 'DEPORTATION'].includes(t)) return 'ev-violence';
  if (t === 'MIGRATION') return 'ev-culture';
  if (['EARTHQUAKE', 'VOLCANIC_ERUPTION', 'TSUNAMI', 'FLOOD', 'DROUGHT', 'FIRE', 'FAMINE', 'EPIDEMIC'].includes(t)) return 'ev-disaster';
  if (['RELIGIOUS_EVENT', 'INTELLECTUAL_EVENT', 'TECHNOLOGICAL_EVENT'].includes(t)) return 'ev-culture';
  return 'ev-other';
}

async function loadEventsForMap(year) {
  if (eventsOverlayCache[year]) return eventsOverlayCache[year];
  try {
    const res = await fetch(`${API}/v1/events/map?year=${year}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    eventsOverlayCache[year] = data.events || [];
    return eventsOverlayCache[year];
  } catch (err) {
    console.warn('Events overlay load failed:', err);
    return [];
  }
}

function renderEventsOverlay() {
  if (!eventsOverlayLayer) return;
  eventsOverlayLayer.clearLayers();
  if (!eventsOverlayEnabled) return;

  const year = parseInt(document.getElementById('year-slider').value, 10);

  loadEventsForMap(year).then(events => {
    eventsOverlayLayer.clearLayers();
    events.forEach(ev => {
      if (ev.location_lat == null || ev.location_lon == null) return;
      const cls = eventTypeClass(ev.event_type);
      const icon = EVENT_TYPE_ICONS[ev.event_type] || '📌';

      const marker = L.marker([ev.location_lat, ev.location_lon], {
        icon: L.divIcon({
          className: '',
          html: `<div class="event-marker-icon ${cls}" title="${esc(ev.name_original)}">${icon}</div>`,
          iconSize: [22, 22],
          iconAnchor: [11, 11],
        }),
        zIndexOffset: 500,
      });

      marker.bindTooltip(eventTooltip(ev), { direction: 'top', offset: [0, -14] });
      marker.on('click', () => showEventPopup(ev));
      eventsOverlayLayer.addLayer(marker);
    });

    // Ensure layer is on map
    if (!map.hasLayer(eventsOverlayLayer)) eventsOverlayLayer.addTo(map);

    // Update count in badge
    const badge = document.getElementById('map-year-badge');
    if (badge && events.length > 0) {
      const existing = badge.innerHTML;
      if (!existing.includes('ev-count')) {
        badge.innerHTML += ` · <span class="ev-count">${events.length} ${t('events')}</span>`;
      } else {
        badge.querySelector('.ev-count').textContent = `${events.length} ${t('events')}`;
      }
    }
  });
}

function eventTooltip(ev) {
  const icon = EVENT_TYPE_ICONS[ev.event_type] || '📌';
  const cls = eventTypeClass(ev.event_type);
  return `
    <div style="min-width:160px">
      <strong>${icon} ${esc(ev.name_original)}</strong><br>
      <span style="font-size:0.85em;opacity:0.85">${fmtY(ev.year)}${ev.location_name ? ' · ' + esc(ev.location_name) : ''}</span><br>
      <span style="font-size:0.78em;opacity:0.7">${ev.event_type ? ev.event_type.replace(/_/g, ' ') : ''}</span>
    </div>`;
}

function showEventPopup(ev) {
  const cls = eventTypeClass(ev.event_type);
  const icon = EVENT_TYPE_ICONS[ev.event_type] || '📌';
  const html = `
    <div class="event-popup-body">
      <div class="ev-popup-title">${icon} ${esc(ev.name_original)}</div>
      <div class="ev-popup-meta">
        <span class="ev-popup-type ${cls}">${ev.event_type ? ev.event_type.replace(/_/g, ' ') : ''}</span>
        <span>${fmtY(ev.year)}</span>
        ${ev.location_name ? `<span>${esc(ev.location_name)}</span>` : ''}
      </div>
      ${ev.main_actor ? `<div class="ev-popup-actor">${t('event_actor')}: ${esc(ev.main_actor)}</div>` : ''}
      <div class="ev-popup-link" onclick="showEventDetail(${ev.id})">${t('event_detail')} →</div>
    </div>`;

  L.popup({ maxWidth: 300, className: 'event-popup' })
    .setLatLng([ev.location_lat, ev.location_lon])
    .setContent(html)
    .openOn(map);
}

async function showEventDetail(eventId) {
  map.closePopup();
  const panel = document.getElementById('detail-panel');
  const content = document.getElementById('detail-content');
  panel.classList.remove('hidden');
  content.innerHTML = '<div class="detail-spinner"><div class="spinner"></div></div>';

  try {
    const res = await fetch(`${API}/v1/events/${eventId}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const ev = await res.json();

    const cls = eventTypeClass(ev.event_type);
    const icon = EVENT_TYPE_ICONS[ev.event_type] || '📌';
    const pct = Math.round((ev.confidence_score || 0) * 100);
    const statusColor = COLORS[ev.status] || '#8b949e';

    content.innerHTML = `
      <h2>${icon} ${esc(ev.name_original)}</h2>
      <div class="detail-meta">
        <span class="ev-popup-type ${cls}">${ev.event_type ? ev.event_type.replace(/_/g, ' ') : ''}</span>
        <span class="status-badge ${ev.status}">${t(ev.status || 'confirmed')}</span>
        <span>${pct}%</span>
      </div>

      <div class="detail-section">
        <div class="detail-row"><span class="label">${t('event_year')}:</span> ${fmtY(ev.year)}${ev.year_end ? ' – ' + fmtY(ev.year_end) : ''}</div>
        ${ev.month ? `<div class="detail-row"><span class="label">${t('event_date')}:</span> ${ev.day || '?'}/${ev.month}/${Math.abs(ev.year)} ${ev.year < 0 ? 'BCE' : 'CE'}</div>` : ''}
        ${ev.location_name ? `<div class="detail-row"><span class="label">${t('event_location')}:</span> ${esc(ev.location_name)}</div>` : ''}
        ${ev.main_actor ? `<div class="detail-row"><span class="label">${t('event_main_actor')}:</span> ${esc(ev.main_actor)}</div>` : ''}
      </div>

      ${ev.description ? `
      <div class="detail-section">
        <h3>${t('event_description')}</h3>
        <p style="font-size:0.85em;line-height:1.55;color:var(--text-muted)">${esc(ev.description)}</p>
      </div>` : ''}

      ${ev.casualties_low || ev.casualties_high ? `
      <div class="detail-section">
        <h3>${t('event_casualties')}</h3>
        <div class="detail-row">
          ${ev.casualties_low ? ev.casualties_low.toLocaleString() : '?'} – ${ev.casualties_high ? ev.casualties_high.toLocaleString() : '?'}
          ${ev.casualties_source ? `<span style="font-size:0.75em;color:var(--text-muted)"> (${esc(ev.casualties_source)})</span>` : ''}
        </div>
      </div>` : ''}

      ${ev.entity_links && ev.entity_links.length ? `
      <div class="detail-section">
        <h3>${t('event_linked_entities')}</h3>
        ${ev.entity_links.map(link => `
          <div class="detail-row" style="cursor:pointer" onclick="showDetail(${link.entity_id})">
            <span class="label">${link.role ? link.role.replace(/_/g, ' ') : ''}:</span>
            <span style="color:var(--accent)">${esc(link.entity_name || 'Entity #' + link.entity_id)}</span>
          </div>
        `).join('')}
      </div>` : ''}

      ${ev.ethical_notes ? `
      <div class="detail-section">
        <div class="ethics-box">
          <strong>ETHICS:</strong> ${esc(ev.ethical_notes)}
        </div>
      </div>` : ''}

      ${ev.sources && ev.sources.length ? `
      <div class="detail-section">
        <h3>${t('sources_section')}</h3>
        <ul style="font-size:0.78em;color:var(--text-muted);padding-left:16px">
          ${ev.sources.map(s => `<li>${esc(s.citation)}${s.url ? ` <a href="${esc(s.url)}" target="_blank" rel="noopener" style="color:var(--accent)">↗</a>` : ''}</li>`).join('')}
        </ul>
      </div>` : ''}
    `;
  } catch (err) {
    content.innerHTML = `<p class="placeholder">${t('event_error')}</p>`;
  }
}

function toggleEventsOverlay(enabled) {
  eventsOverlayEnabled = !!enabled;
  const legend = document.getElementById('events-overlay-legend');
  if (legend) legend.classList.toggle('hidden', !eventsOverlayEnabled);

  if (!eventsOverlayEnabled) {
    if (eventsOverlayLayer) eventsOverlayLayer.clearLayers();
    // Remove event count from badge
    const badge = document.getElementById('map-year-badge');
    if (badge) {
      const evCount = badge.querySelector('.ev-count');
      if (evCount) {
        // Remove " · " before the span too
        const text = badge.innerHTML;
        badge.innerHTML = text.replace(/ · <span class="ev-count">.*?<\/span>/, '');
      }
    }
    return;
  }

  renderEventsOverlay();
}

// ─── Dynasty Chains sidebar (v6.7, Feature 2) ─────────────────

async function loadChains() {
  const listEl = document.getElementById('chains-list');
  const countEl = document.getElementById('chains-count');
  try {
    const res = await fetch(`${API}/v1/chains`, { cache: 'no-cache' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    chainsData = Array.isArray(data) ? data : (data.chains || data.items || []);
    if (countEl) countEl.textContent = `(${chainsData.length})`;
    renderChainsList();
  } catch (err) {
    if (listEl) listEl.innerHTML = `<div class="chains-placeholder">${lang === 'it' ? 'Catene non disponibili.' : 'Chains not available.'}</div>`;
    if (countEl) countEl.textContent = '';
  }
}

function renderChainsList() {
  const listEl = document.getElementById('chains-list');
  if (!listEl || !chainsData) return;
  if (!chainsData.length) {
    listEl.innerHTML = `<div class="chains-placeholder">${lang === 'it' ? 'Nessuna catena.' : 'No chains.'}</div>`;
    return;
  }

  listEl.innerHTML = chainsData.map(c => {
    const name = esc(c.name || '—');
    const ctype = esc(c.chain_type || '—');
    const links = (typeof c.link_count === 'number') ? c.link_count
      : (Array.isArray(c.links) ? c.links.length : '?');
    const region = esc(c.region || '—');
    const isIdeological = (c.chain_type || '').toUpperCase() === 'IDEOLOGICAL';
    return `
    <div class="chain-card${isIdeological ? ' chain-ideological' : ''}" data-id="${c.id}" role="listitem" tabindex="0"
         aria-label="Catena ${name}, tipo ${ctype}, ${links} link">
      <div class="chain-card-header">
        <span class="chain-card-name">${name}</span>
        ${isIdeological ? '<span class="chain-ideo-badge" title="Continuità self-proclaimed — vedi ETHICS-003">ETHICS-003</span>' : ''}
      </div>
      <div class="chain-card-meta">
        <span class="chain-type-tag">${ctype}</span>
        <span class="chain-link-count">${links} link</span>
        <span class="chain-region">${region}</span>
      </div>
    </div>`;
  }).join('');

  listEl.querySelectorAll('.chain-card').forEach(card => {
    const handler = () => showChainDetail(card.dataset.id);
    card.addEventListener('click', handler);
    card.addEventListener('keydown', ev => { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); handler(); } });
  });
}

async function loadChainDetail(id) {
  if (chainDetailCache[id]) return chainDetailCache[id];
  try {
    const res = await fetch(`${API}/v1/chains/${id}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    chainDetailCache[id] = data;
    return data;
  } catch (err) {
    showError(lang === 'it' ? 'Errore nel caricamento della catena.' : 'Error loading chain.');
    return null;
  }
}

async function showChainDetail(id) {
  const panel = document.getElementById('detail-panel');
  const content = document.getElementById('detail-content');
  panel.classList.remove('hidden');
  content.innerHTML = '<div class="detail-spinner"><div class="spinner"></div></div>';

  // Clear entity context — we're showing a chain, not an entity
  currentDetailEntity = null;
  currentDetailTab = 'overview';

  if (window.innerWidth <= 768) {
    document.getElementById('sidebar').classList.add('collapsed');
  }
  const info = document.getElementById('map-info');
  if (info) info.style.display = 'none';

  const chain = await loadChainDetail(id);
  if (!chain) { panel.classList.add('hidden'); return; }

  const isIdeological = (chain.chain_type || '').toUpperCase() === 'IDEOLOGICAL';
  const links = chain.links || chain.sequence || [];

  // ETHICS-003: self-proclaimed ideological continuity must show a
  // warning banner; otherwise the UI would endorse the myth as fact.
  const banner = isIdeological ? `
    <div class="chain-ethics-banner" role="note">
      <strong>${lang === 'it' ? 'Continuità self-proclaimed' : 'Self-proclaimed continuity'}</strong>
      ${lang === 'it'
        ? ' — questa catena è una rivendicazione ideologica di continuità, non una discendenza storica verificata. Vedi ETHICS-003.'
        : ' — this chain represents a self-proclaimed ideological continuity, not a verified historical lineage. See ETHICS-003.'}
    </div>` : '';

  let html = `
    <h2 class="chain-detail-title">${esc(chain.name || '—')}</h2>
    <div class="detail-tags">
      <span class="chain-type-tag">${esc(chain.chain_type || '—')}</span>
      ${chain.region ? `<span class="continent-tag">${esc(chain.region)}</span>` : ''}
      <span class="lang-tag">${links.length} link</span>
    </div>
    ${banner}
    ${chain.description ? `<p class="chain-description">${esc(chain.description)}</p>` : ''}

    <div class="detail-section">
      <h3 class="collapsible" tabindex="0">${lang === 'it' ? 'Sequenza di link' : 'Link sequence'} <span class="collapse-icon">▾</span></h3>
      <div class="section-body">
        ${renderChainTimeline(links)}
      </div>
    </div>
    ${chain.ethical_notes ? `
      <div class="detail-section">
        <h3 class="collapsible" tabindex="0">${lang === 'it' ? 'Governance etica' : 'Ethical governance'} <span class="collapse-icon">▾</span></h3>
        <div class="section-body">
          <div class="ethics-box">${esc(chain.ethical_notes)}</div>
        </div>
      </div>` : ''}
  `;

  content.innerHTML = html;

  content.querySelectorAll('.collapsible').forEach(h3 => {
    h3.addEventListener('click', () => toggleSection(h3));
    h3.addEventListener('keydown', ev => { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); toggleSection(h3); } });
  });

  content.querySelectorAll('.chain-link-entity[data-entity-id]').forEach(el => {
    const eid = +el.dataset.entityId;
    if (!eid) return;
    const handler = () => showDetail(eid);
    el.addEventListener('click', handler);
    el.addEventListener('keydown', ev => { if (ev.key === 'Enter') handler(); });
  });
}

function renderChainTimeline(links) {
  if (!Array.isArray(links) || !links.length) {
    return `<p class="placeholder">${lang === 'it' ? 'Nessun link disponibile.' : 'No links available.'}</p>`;
  }
  return `
    <ol class="chain-timeline">
      ${links.map((l, i) => {
        const eid = l.entity_id || (l.entity && l.entity.id);
        const ename = l.entity_name || (l.entity && l.entity.name_original) || l.name || `#${eid || i + 1}`;
        const ttype = l.transition_type ? esc(l.transition_type.replace(/_/g, ' ')) : '';
        const tyear = (l.transition_year != null) ? fmtY(l.transition_year) : '';
        const desc = l.description || l.transition_description || '';
        const clickable = !!eid;
        return `
        <li class="chain-timeline-item">
          <div class="chain-timeline-marker" aria-hidden="true">${i + 1}</div>
          <div class="chain-timeline-content">
            <div class="chain-link-entity${clickable ? ' clickable' : ''}" ${clickable ? `data-entity-id="${eid}" tabindex="0" role="button"` : ''}>
              ${esc(ename)}
            </div>
            <div class="chain-link-meta">
              ${tyear ? `<span class="chain-link-year">${tyear}</span>` : ''}
              ${ttype ? `<span class="chain-link-type">${ttype}</span>` : ''}
            </div>
            ${desc ? `<div class="chain-link-desc">${esc(desc)}</div>` : ''}
          </div>
        </li>`;
      }).join('')}
    </ol>`;
}

// ─── Autocomplete ──────────────────────────────────────────────

function showAutocomplete(query) {
  const dropdown = document.getElementById('autocomplete-list');
  const input = document.getElementById('search-input');

  if (!query || query.length < 2) {
    hideAutocomplete();
    return;
  }

  const q = query.toLowerCase();
  const matches = allEntities
    .filter(e => {
      const inName = e.name_original.toLowerCase().includes(q);
      const inVar = (e.name_variants || []).some(v => v.name.toLowerCase().includes(q));
      return inName || inVar;
    })
    .slice(0, 8);

  if (!matches.length) {
    dropdown.innerHTML = `<div class="autocomplete-hint">${t('no_results')}</div>`;
    dropdown.classList.add('visible');
    input.setAttribute('aria-expanded', 'true');
    acSelectedIndex = -1;
    return;
  }

  dropdown.innerHTML = matches.map((e, i) => {
    const icon = TYPE_ICONS[e.entity_type] || '\ud83d\udccd';
    const pct = Math.round(e.confidence_score * 100);
    const name = highlightMatch(e.name_original, query);
    const matchedVar = (e.name_variants || []).find(v => v.name.toLowerCase().includes(q));
    const variantHint = matchedVar && !e.name_original.toLowerCase().includes(q)
      ? ` <span style="color:var(--accent);font-size:0.85em">\u2190 ${esc(matchedVar.name)}</span>` : '';
    return `<div class="autocomplete-item" data-id="${e.id}" data-idx="${i}" role="option" tabindex="-1">
      <span class="ac-icon">${icon}</span>
      <div class="ac-info">
        <div class="ac-name">${name}${variantHint}</div>
        <div class="ac-meta">${e.entity_type} \u00b7 ${fmtY(e.year_start)}\u2013${e.year_end ? fmtY(e.year_end) : t('today')}</div>
      </div>
      <span class="ac-score">${pct}%</span>
    </div>`;
  }).join('') + `<div class="autocomplete-hint">\u21b5 ${t('enter_to_search') || 'Invio per cercare'} \u00b7 \u2191\u2193 ${t('navigate') || 'naviga'}</div>`;

  dropdown.classList.add('visible');
  input.setAttribute('aria-expanded', 'true');
  acSelectedIndex = -1;

  // v6.66 FIX 3: il click sull'item dropdown deve aprire il detail panel
  // e fare la fetch a /v1/entities/{id}. Bug precedente: usando solo
  // 'mousedown' il preventDefault evitava il blur sull'input, MA se la
  // fetch falliva non c'era error-handling visibile e lo spinner restava.
  // Nuovo approccio:
  //  - event delegation sul parent dropdown (sopravvive a re-render)
  //  - mousedown preventDefault (per non perdere il focus prima del click)
  //  - chiama direttamente showDetail(id) con l'id number coerced
  //  - reset spinner on error nella catena showDetail/loadDetail
  const handleItemActivation = (ev) => {
    const item = ev.target.closest('.autocomplete-item');
    if (!item) return;
    ev.preventDefault();
    ev.stopPropagation();
    const id = Number(item.dataset.id);
    if (!Number.isFinite(id)) return;
    // Chiudiamo il dropdown DOPO aver avviato la fetch, così il blur
    // dell'input non ruba il focus prima del tempo.
    showDetail(id);
    hideAutocomplete();
    // Sposta il focus sul panel per accessibilità
    const panel = document.getElementById('detail-panel');
    if (panel) panel.setAttribute('tabindex', '-1');
  };
  // Rimuoviamo eventuali listener pregressi (safe: null se primo setup)
  if (dropdown.__acHandler) {
    dropdown.removeEventListener('mousedown', dropdown.__acHandler);
    dropdown.removeEventListener('click', dropdown.__acHandler);
  }
  dropdown.__acHandler = handleItemActivation;
  dropdown.addEventListener('mousedown', handleItemActivation);
  // Click come fallback (touch, alcuni a11y tool che non sparano mousedown)
  dropdown.addEventListener('click', handleItemActivation);
}

function hideAutocomplete() {
  const dropdown = document.getElementById('autocomplete-list');
  const input = document.getElementById('search-input');
  dropdown.classList.remove('visible');
  input.setAttribute('aria-expanded', 'false');
  acSelectedIndex = -1;
}

function navigateAutocomplete(dir) {
  const items = document.querySelectorAll('.autocomplete-item');
  if (!items.length) return;

  items.forEach(i => i.classList.remove('ac-active'));
  acSelectedIndex += dir;
  if (acSelectedIndex < 0) acSelectedIndex = items.length - 1;
  if (acSelectedIndex >= items.length) acSelectedIndex = 0;

  items[acSelectedIndex].classList.add('ac-active');
  items[acSelectedIndex].scrollIntoView({ block: 'nearest' });
}

function selectAutocompleteItem() {
  const items = document.querySelectorAll('.autocomplete-item');
  if (acSelectedIndex >= 0 && acSelectedIndex < items.length) {
    showDetail(+items[acSelectedIndex].dataset.id);
    hideAutocomplete();
    return true;
  }
  return false;
}

function highlightMatch(text, query) {
  if (!query) return esc(text);
  const escaped = esc(text);
  const q = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const regex = new RegExp(`(${q})`, 'gi');
  return escaped.replace(regex, '<mark>$1</mark>');
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

  // v6.66 FIX: aggiorna il counter header (prima mostrava solo allEntities.length,
  // ora mostra filtered/total così lo stato filtri è sempre visibile).
  // ETHICS: trasparenza — l'utente deve sapere quante entità sta vedendo davvero.
  const badgeCount = document.getElementById('entity-count');
  if (badgeCount) {
    if (filtered.length === allEntities.length) {
      badgeCount.textContent = `${allEntities.length} ${t('entities')}`;
    } else {
      badgeCount.textContent = `${filtered.length} / ${allEntities.length} ${t('entities')}`;
    }
  }
  // v6.66: esponi risultato filtrato per "Zoom su tutte" (map-fit-all),
  // così il bottone considera il filtro attivo invece di allEntities.
  window.__lastFiltered = filtered;

  // Update map year badge
  const yearBadge = document.getElementById('map-year-badge');
  if (yearBadge) {
    yearBadge.innerHTML = `<span class="year-value">${fmtY(year)}</span> \u00b7 <span class="entity-count">${filtered.length}</span> ${t('entities')}`;
  }
}

// ─── Lista risultati ────────────────────────────────────────────

function renderResults(entities) {
  const el = document.getElementById('results-list');
  const countEl = document.getElementById('on-map-count');
  if (countEl) countEl.textContent = entities.length.toLocaleString('en-US').replace(/,/g, '.');

  if (!entities.length) {
    el.innerHTML = `<p class="placeholder">${t('no_results')}</p>`;
    return;
  }

  // v6.90: editorial entity-row layout (spec §3). Swatch usa HSL per-id (hashHue).
  el.innerHTML = entities.map((e, idx) => {
    const hue = hashHue(e.id);
    const rangeEnd = e.year_end ? fmtY(e.year_end) : t('today');
    const range = `${fmtY(e.year_start)}\u2013${rangeEnd}`;
    return `
    <div class="entity-row result-card ${e.status}" data-id="${e.id}" data-idx="${idx}" role="listitem" tabindex="0">
      <span class="swatch" style="background:hsl(${hue}, 55%, 55%)" aria-hidden="true"></span>
      <span class="entity-row__name">${esc(e.name_original)}</span>
      <span class="range">${range}</span>
    </div>`;
  }).join('');

  // v6.90: dual-class .entity-row .result-card — preserva tutti i querySelector
  // esistenti (.result-card in compare, scroll, keyboard navigation) intatti.
  el.querySelectorAll('.entity-row').forEach(row => {
    const handler = () => showDetail(+row.dataset.id);
    row.addEventListener('click', handler);
    row.addEventListener('keydown', ev => { if (ev.key === 'Enter') handler(); });
  });
}

// v6.90: hashHue helper — djb2 hash → HSL hue (0-359). ETICHICS-011: stateless,
// no gerarchie culturali. Shared con renderMap (Phase 2.6) via window.hashHue.
function hashHue(id) {
  let h = 0;
  const s = String(id);
  for (let i = 0; i < s.length; i++) h = ((h << 5) - h) + s.charCodeAt(i);
  return Math.abs(h) % 360;
}
window.hashHue = hashHue;

// ─── Mappa ──────────────────────────────────────────────────────

function renderMap(entities) {
  layerGroup.clearLayers();

  // Cluster group for capital-only markers (no GeoJSON boundary)
  const clusterGroup = typeof L.markerClusterGroup === 'function'
    ? L.markerClusterGroup({
        maxClusterRadius: 40,
        spiderfyOnMaxZoom: true,
        showCoverageOnHover: false,
        iconCreateFunction: cluster => {
          const count = cluster.getChildCount();
          const size = count < 10 ? 'small' : count < 50 ? 'medium' : 'large';
          return L.divIcon({
            html: `<div class="cluster-icon cluster-${size}">${count}</div>`,
            className: 'marker-cluster-custom',
            iconSize: L.point(36, 36),
          });
        },
      })
    : L.layerGroup(); // fallback if plugin not loaded

  entities.forEach(e => {
    const c = COLORS[e.status] || '#8b949e';
    try {
      const geo = e.boundary_geojson;

      if (geo && geo.type === 'Point') {
        const [lon, lat] = geo.coordinates;
        const m = L.circleMarker([lat, lon], {
          radius: 8, fillColor: c, color: '#fff', weight: 1.5, fillOpacity: 0.85,
        });
        m.bindTooltip(richTooltip(e), { direction: 'top' });
        m.on('click', () => showDetail(e.id));
        layerGroup.addLayer(m);
      } else if (geo && (geo.type === 'Polygon' || geo.type === 'MultiPolygon')) {
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
      } else if (e.capital && e.capital.lat && e.capital.lon) {
        // No boundary GeoJSON — show capital as a clustered marker
        const m = L.circleMarker([e.capital.lat, e.capital.lon], {
          radius: 5, fillColor: c, color: c, weight: 1, fillOpacity: 0.7,
          className: 'capital-marker',
        });
        m.bindTooltip(richTooltip(e), { direction: 'top' });
        m.on('click', () => showDetail(e.id));
        clusterGroup.addLayer(m);

        // Label for larger zoom levels
        clusterGroup.addLayer(L.marker([e.capital.lat, e.capital.lon], {
          icon: L.divIcon({
            className: 'capital-label',
            html: `<div style="color:${c};font-size:9px;font-weight:500;text-shadow:0 0 3px #000,0 0 2px #000;white-space:nowrap;pointer-events:none;opacity:0.8">${esc(e.name_original)}</div>`,
            iconSize: null, iconAnchor: [-6, 3],
          }),
          interactive: false,
        }));
      }
    } catch (_) {}
  });

  layerGroup.addLayer(clusterGroup);
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
  // v6.66 FIX 3: se loadDetail fallisce, sostituiamo lo spinner con un
  // messaggio d'errore leggibile invece di lasciare lo spinner infinito.
  if (!e) {
    content.innerHTML = `<p class="placeholder">${t('error_detail') || 'Errore nel caricamento dei dettagli.'}</p>`;
    return;
  }

  // v6.7 — remember current entity for tab switching (Feature 3)
  currentDetailEntity = e;
  currentDetailTab = 'overview';

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

    <div class="detail-tabs" role="tablist" aria-label="${lang === 'it' ? 'Viste dettaglio entit\u00e0' : 'Entity detail views'}">
      <button class="detail-tab active" role="tab" aria-selected="true" aria-controls="detail-tab-overview" data-tab="overview">
        ${lang === 'it' ? 'Panoramica' : 'Overview'}
      </button>
      <button class="detail-tab" role="tab" aria-selected="false" aria-controls="detail-tab-timeline" data-tab="timeline">
        ${lang === 'it' ? 'Timeline unificata' : 'Unified timeline'}
      </button>
    </div>

    <div class="detail-tab-panel" id="detail-tab-overview" role="tabpanel" aria-labelledby="overview">

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

  // v6.88: capital_history timeline (ADR-004)
  // Per polities long-duration con capitali multiple: mostra cronologia
  // Ordine: per year_start ASC, poi ordering ASC (per casi sovrapposti es. dual monarchy)
  if (Array.isArray(e.capital_history) && e.capital_history.length > 0) {
    const ch = [...e.capital_history].sort((a, b) =>
      (a.year_start - b.year_start) || (a.ordering - b.ordering)
    );
    const titleIT = 'Cronologia capitali';
    const titleEN = 'Capital history';
    const subIT = 'Capitali multiple per polity long-duration (ADR-004). Useful for AI agents querying "capital of X in year Y".';
    const subEN = 'Multiple capitals for long-duration polities (ADR-004). Useful for AI agents querying "capital of X in year Y".';
    html += `
    <div class="detail-section" data-section="capital-history">
      <h3 class="collapsible" tabindex="0">${lang === 'it' ? titleIT : titleEN} <span class="collapse-icon">▾</span></h3>
      <div class="section-body">
        <p style="font-size:0.78em;color:var(--text-muted);margin:0 0 8px 0">${lang === 'it' ? subIT : subEN}</p>
        <ol class="capital-history-list" style="list-style:none;padding-left:0;margin:0">
          ${ch.map(c => {
            const period = c.year_end != null
              ? `${fmtY(c.year_start)} \u2013 ${fmtY(c.year_end)}`
              : `${fmtY(c.year_start)} \u2013 ${lang === 'it' ? 'oggi/ultima' : 'today/last'}`;
            const coords = (c.lat != null && c.lon != null)
              ? ` <span class="geo-micro">(${c.lat.toFixed(2)}\u00b0, ${c.lon.toFixed(2)}\u00b0)</span>`
              : ` <span class="geo-micro">(${lang === 'it' ? 'corte itinerante' : 'court itinerant'})</span>`;
            const notes = c.notes ? `<br><span style="font-size:0.78em;color:var(--text-muted)">${esc(c.notes)}</span>` : '';
            return `
              <li style="padding:6px 8px;margin-bottom:4px;border-left:2px solid var(--accent);background:rgba(88,166,255,0.06)">
                <strong>${esc(c.name)}</strong>${coords}<br>
                <span style="font-size:0.82em;color:var(--text-muted)">${period}</span>
                ${notes}
              </li>`;
          }).join('')}
        </ol>
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

  // Mini-timeline canvas (v5.8)
  if (e.year_start != null) {
    html += `
    <div class="mini-timeline-container">
      <h4>${lang === 'it' ? 'Timeline' : 'Timeline'}: ${fmtY(e.year_start)} – ${e.year_end ? fmtY(e.year_end) : (lang === 'it' ? 'oggi' : 'today')}</h4>
      <canvas class="mini-timeline-canvas" id="mini-timeline" width="600" height="60"></canvas>
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

  // Close overview tab panel and add timeline tab panel (hidden until selected)
  html += `
    </div><!-- /#detail-tab-overview -->
    <div class="detail-tab-panel hidden" id="detail-tab-timeline" role="tabpanel" aria-labelledby="timeline">
      <div class="unified-timeline-loading">
        <div class="detail-spinner" style="height:100px"><div class="spinner" style="width:24px;height:24px"></div></div>
      </div>
    </div>`;

  content.innerHTML = html;

  // Bind tab switching
  content.querySelectorAll('.detail-tab').forEach(tab => {
    tab.addEventListener('click', () => switchDetailTab(tab.dataset.tab));
    tab.addEventListener('keydown', ev => {
      if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); switchDetailTab(tab.dataset.tab); }
    });
  });

  // Draw mini-timeline canvas (v5.8 + v6.51 event markers)
  drawMiniTimeline(e);

  // v6.51: async-load events linked to this entity and redraw timeline
  // with additional event markers (red dots, distinct from territory_changes diamonds).
  (async () => {
    try {
      const evRes = await fetch(`${API}/v1/entities/${id}/events`);
      if (!evRes.ok) return;
      const evData = await evRes.json();
      const events = evData.events || evData.items || [];
      if (events.length > 0) {
        drawMiniTimeline(e, events);
      }
    } catch (_) {
      // Silent fail — timeline still shows territory_changes
    }
  })();

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

// ─── Detail panel tab switching + unified timeline (v6.7, Feature 3) ──

function switchDetailTab(tab) {
  if (!tab) return;
  currentDetailTab = tab;

  const content = document.getElementById('detail-content');
  if (!content) return;

  content.querySelectorAll('.detail-tab').forEach(t => {
    const active = t.dataset.tab === tab;
    t.classList.toggle('active', active);
    t.setAttribute('aria-selected', active ? 'true' : 'false');
  });

  content.querySelectorAll('.detail-tab-panel').forEach(p => {
    p.classList.toggle('hidden', p.id !== `detail-tab-${tab}`);
  });

  if (tab === 'timeline' && currentDetailEntity) {
    loadUnifiedTimeline(currentDetailEntity.id);
  }
}

async function loadUnifiedTimeline(entityId) {
  const panel = document.getElementById('detail-tab-timeline');
  if (!panel) return;

  // If we've already rendered for this entity, don't refetch
  if (panel.dataset.loadedFor === String(entityId)) return;

  panel.innerHTML = `<div class="detail-spinner" style="height:100px"><div class="spinner" style="width:24px;height:24px"></div></div>`;

  try {
    const res = await fetch(`${API}/v1/entities/${entityId}/timeline`);
    if (res.status === 404) {
      panel.innerHTML = `
        <div class="unified-timeline-unavailable">
          <p>${lang === 'it'
            ? 'Timeline endpoint non disponibile su questa versione.'
            : 'Timeline endpoint not available on this version.'}</p>
          <p style="font-size:0.78em;color:var(--text-muted);margin-top:6px">
            ${lang === 'it'
              ? 'La timeline unificata sar\u00e0 disponibile in una versione futura (v6.8+).'
              : 'The unified timeline will be available in a future version (v6.8+).'}
          </p>
        </div>`;
      panel.dataset.loadedFor = String(entityId);
      return;
    }
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    renderUnifiedTimeline(panel, data);
    panel.dataset.loadedFor = String(entityId);
  } catch (err) {
    panel.innerHTML = `
      <div class="unified-timeline-unavailable">
        <p>${lang === 'it' ? 'Errore nel caricamento della timeline.' : 'Error loading timeline.'}</p>
        <p style="font-size:0.78em;color:var(--text-muted);margin-top:6px">${esc(err.message || '')}</p>
      </div>`;
  }
}

function renderUnifiedTimeline(panel, data) {
  // Accept multiple response shapes:
  //   { events: [...], territory_changes: [...], chain_transitions: [...] }
  //   { items: [{kind, year, ...}] }  (pre-merged)
  let items = [];
  if (Array.isArray(data)) {
    items = data.slice();
  } else if (Array.isArray(data.items)) {
    items = data.items.slice();
  } else {
    (data.events || []).forEach(ev => items.push({
      kind: 'event',
      year: ev.year ?? ev.start_year ?? ev.date,
      title: ev.name || ev.title,
      description: ev.description,
      event_type: ev.event_type || ev.type,
      raw: ev,
    }));
    (data.territory_changes || []).forEach(tc => items.push({
      kind: 'territory_change',
      year: tc.year,
      title: tc.change_type ? tc.change_type.replace(/_/g, ' ') : 'Territory change',
      description: tc.description,
      region: tc.region,
      population_affected: tc.population_affected,
      raw: tc,
    }));
    (data.chain_transitions || []).forEach(ct => items.push({
      kind: 'chain_transition',
      year: ct.transition_year ?? ct.year,
      title: ct.transition_type ? ct.transition_type.replace(/_/g, ' ') : 'Chain transition',
      description: ct.description,
      chain_name: ct.chain_name,
      chain_id: ct.chain_id,
      raw: ct,
    }));
  }

  // Sort chronologically (null years pushed to the end)
  items.sort((a, b) => {
    if (a.year == null && b.year == null) return 0;
    if (a.year == null) return 1;
    if (b.year == null) return -1;
    return a.year - b.year;
  });

  if (!items.length) {
    panel.innerHTML = `<p class="placeholder">${lang === 'it' ? 'Nessun evento storico registrato.' : 'No historical events recorded.'}</p>`;
    return;
  }

  const kindIcon = {
    event: '📅',
    territory_change: '🗺️',
    chain_transition: '🔗',
  };
  const kindLabel = lang === 'it'
    ? { event: 'Evento', territory_change: 'Territorio', chain_transition: 'Catena' }
    : { event: 'Event', territory_change: 'Territory', chain_transition: 'Chain' };

  panel.innerHTML = `
    <h3 class="unified-timeline-heading">${lang === 'it' ? 'Eventi, territorio e transizioni' : 'Events, territory and transitions'}</h3>
    <ol class="unified-timeline">
      ${items.map(it => {
        const icon = kindIcon[it.kind] || '•';
        const label = kindLabel[it.kind] || it.kind;
        const year = it.year != null ? fmtY(it.year) : '?';
        const title = esc(it.title || label);
        const desc = it.description ? esc(it.description) : '';
        const extra = [];
        if (it.region) extra.push(esc(it.region));
        if (it.population_affected) extra.push(`~${Number(it.population_affected).toLocaleString('it-IT')} ${lang === 'it' ? 'persone' : 'people'}`);
        if (it.chain_name) extra.push(`${lang === 'it' ? 'Catena' : 'Chain'}: ${esc(it.chain_name)}`);

        return `
        <li class="utl-item utl-${it.kind}">
          <div class="utl-marker" aria-hidden="true">${icon}</div>
          <div class="utl-body">
            <div class="utl-header">
              <span class="utl-year">${year}</span>
              <span class="utl-kind">${label}</span>
              <span class="utl-title">${title}</span>
            </div>
            ${desc ? `<div class="utl-desc">${desc}</div>` : ''}
            ${extra.length ? `<div class="utl-extra">${extra.join(' · ')}</div>` : ''}
          </div>
        </li>`;
      }).join('')}
    </ol>`;
}

function drawMiniTimeline(e, events) {
  // v6.51: events param optional — red circular markers for HistoricalEvent linked
  const canvas = document.getElementById('mini-timeline');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const dpr = window.devicePixelRatio || 1;

  // Size canvas properly
  const rect = canvas.parentElement.getBoundingClientRect();
  canvas.width = rect.width * dpr;
  canvas.height = 60 * dpr;
  canvas.style.width = rect.width + 'px';
  canvas.style.height = '60px';
  ctx.scale(dpr, dpr);

  const W = rect.width;
  const H = 60;
  const pad = 30;
  const barY = 25;
  const barH = 12;

  const ys = e.year_start;
  const ye = e.year_end || new Date().getFullYear();
  const span = ye - ys || 1;

  // Background
  ctx.clearRect(0, 0, W, H);

  // Time axis
  ctx.fillStyle = '#30363d';
  ctx.fillRect(pad, barY, W - 2 * pad, barH);

  // Entity lifespan bar
  const sc = COLORS[e.status] || '#58a6ff';
  ctx.fillStyle = sc;
  ctx.globalAlpha = 0.5;
  ctx.fillRect(pad, barY, W - 2 * pad, barH);
  ctx.globalAlpha = 1;

  // Year labels
  ctx.fillStyle = '#8b949e';
  ctx.font = '10px system-ui, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText(fmtY(ys), pad, barY + barH + 14);
  ctx.textAlign = 'right';
  ctx.fillText(fmtY(ye), W - pad, barY + barH + 14);

  // Territory change markers
  const changes = (e.territory_changes || []).slice().sort((a, b) => a.year - b.year);
  const changeColors = {
    expansion: '#3fb950', conquest: '#3fb950',
    contraction: '#da3633', split: '#da3633',
    independence: '#58a6ff', treaty: '#58a6ff',
    colonization: '#d29922', merger: '#d29922',
  };

  const markers = [];
  changes.forEach(tc => {
    const x = pad + ((tc.year - ys) / span) * (W - 2 * pad);
    const color = changeColors[tc.change_type] || '#8b949e';

    // Marker line
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(x, barY - 6);
    ctx.lineTo(x, barY + barH + 6);
    ctx.stroke();

    // Diamond marker
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.moveTo(x, barY - 8);
    ctx.lineTo(x + 4, barY - 4);
    ctx.lineTo(x, barY);
    ctx.lineTo(x - 4, barY - 4);
    ctx.closePath();
    ctx.fill();

    markers.push({ x, year: tc.year, type: tc.change_type, desc: tc.description || '', region: tc.region || '' });
  });

  // v6.51: draw event markers (red circles) BELOW the bar.
  if (Array.isArray(events) && events.length) {
    events.forEach(ev => {
      const evY = ev.year || ev.year_start;
      if (typeof evY !== 'number') return;
      if (evY < ys || evY > ye) return;  // outside entity lifespan
      const x = pad + ((evY - ys) / span) * (W - 2 * pad);

      // Connector line (short, dashed feel via stroke pattern)
      ctx.strokeStyle = 'rgba(248, 81, 73, 0.6)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(x, barY + barH);
      ctx.lineTo(x, barY + barH + 10);
      ctx.stroke();

      // Red circle
      ctx.fillStyle = '#f85149';
      ctx.beginPath();
      ctx.arc(x, barY + barH + 13, 3.5, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = '#1a1a2e';
      ctx.lineWidth = 1;
      ctx.stroke();

      markers.push({
        x,
        year: evY,
        type: 'EVENT',
        desc: ev.name_original || ev.description || '',
        region: ev.event_type || '',
        isEvent: true,
      });
    });
  }

  // Tooltip on hover
  let tooltipDiv = null;
  canvas.addEventListener('mousemove', ev => {
    const bnd = canvas.getBoundingClientRect();
    const mx = ev.clientX - bnd.left;
    const hit = markers.find(m => Math.abs(m.x - mx) < 8);
    if (hit) {
      canvas.style.cursor = 'pointer';
      if (!tooltipDiv) {
        tooltipDiv = document.createElement('div');
        tooltipDiv.style.cssText = 'position:absolute;background:#161b22;border:1px solid #30363d;border-radius:4px;padding:4px 8px;font-size:11px;color:#e6edf3;pointer-events:none;z-index:1000;white-space:nowrap;box-shadow:0 2px 6px rgba(0,0,0,0.4)';
        canvas.parentElement.style.position = 'relative';
        canvas.parentElement.appendChild(tooltipDiv);
      }
      if (hit.isEvent) {
        tooltipDiv.innerHTML = `<strong style="color:#f85149">📍 ${fmtY(hit.year)}</strong> — ${esc(hit.desc)}${hit.region ? ' <small style="color:#888">[' + esc(hit.region) + ']</small>' : ''}`;
      } else {
        tooltipDiv.innerHTML = `<strong>${fmtY(hit.year)}</strong> — ${hit.type.replace(/_/g, ' ')}${hit.region ? ' (' + esc(hit.region) + ')' : ''}`;
      }
      tooltipDiv.style.left = Math.min(hit.x, W - 150) + 'px';
      tooltipDiv.style.top = '-22px';
      tooltipDiv.style.display = 'block';
    } else {
      canvas.style.cursor = 'crosshair';
      if (tooltipDiv) tooltipDiv.style.display = 'none';
    }
  });
  canvas.addEventListener('mouseleave', () => {
    if (tooltipDiv) tooltipDiv.style.display = 'none';
  });
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

  document.getElementById('search-btn').addEventListener('click', () => { hideAutocomplete(); applyFilters(); pushUrlState(); });

  searchInput.addEventListener('keydown', e => {
    const dropdown = document.getElementById('autocomplete-list');
    if (dropdown.classList.contains('visible')) {
      if (e.key === 'ArrowDown') { e.preventDefault(); navigateAutocomplete(1); return; }
      if (e.key === 'ArrowUp') { e.preventDefault(); navigateAutocomplete(-1); return; }
      if (e.key === 'Enter') {
        e.preventDefault();
        if (!selectAutocompleteItem()) { hideAutocomplete(); applyFilters(); pushUrlState(); }
        return;
      }
      if (e.key === 'Escape') { e.preventDefault(); hideAutocomplete(); return; }
    } else if (e.key === 'Enter') {
      applyFilters(); pushUrlState();
    }
  });

  searchInput.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    clearTimeout(acDebounceTimer);
    const val = searchInput.value.trim();
    acDebounceTimer = setTimeout(() => showAutocomplete(val), 150);
    debounceTimer = setTimeout(() => { applyFilters(); pushUrlState(); }, 400);
  });

  searchInput.addEventListener('blur', () => {
    setTimeout(hideAutocomplete, 200);
  });

  searchInput.addEventListener('focus', () => {
    const val = searchInput.value.trim();
    if (val.length >= 2) showAutocomplete(val);
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
  yearSlider.addEventListener('change', () => {
    applyFilters();
    pushUrlState();
    loadSnapshotSummary(+yearSlider.value);
    // v6.23 — refresh events overlay if active
    if (eventsOverlayEnabled) renderEventsOverlay();
    // v6.7 — refresh trade routes if active (they're year-filtered)
    if (tradeRoutesEnabled) renderTradeRoutes();
  });

  function applyYearInput() {
    let val = parseInt(yearInput.value, 10) || 0;
    if (yearEra.value === 'bc') val = -Math.abs(val);
    val = Math.max(-4500, Math.min(2025, val));
    yearSlider.value = val;
    yearDisplay.textContent = fmtY(val);
    applyFilters();
    pushUrlState();
    if (eventsOverlayEnabled) renderEventsOverlay();
    if (tradeRoutesEnabled) renderTradeRoutes();
  }

  document.getElementById('year-go').addEventListener('click', applyYearInput);
  yearInput.addEventListener('keyup', e => { if (e.key === 'Enter') applyYearInput(); });
  yearEra.addEventListener('change', applyYearInput);

  // v6.50: .era-chips replaces .year-presets (narrative preset buttons)
  document.querySelectorAll('.year-presets button, .era-chip').forEach(btn => {
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
      // v6.90: mark era-chip attivo visualmente (single-selection)
      document.querySelectorAll('.era-chip').forEach(c => c.classList.remove('active'));
      if (btn.classList.contains('era-chip')) btn.classList.add('active');
      applyFilters();
      pushUrlState();
      if (eventsOverlayEnabled) renderEventsOverlay();
      if (tradeRoutesEnabled) renderTradeRoutes();
      // v6.90: dispatch input → year-hero + era-ticks update
      yearSlider.dispatchEvent(new Event('input', { bubbles: true }));
    });
  });

  document.querySelectorAll('.checkbox-group input').forEach(cb => {
    cb.addEventListener('change', () => { applyFilters(); pushUrlState(); });
  });

  document.getElementById('sort-select').addEventListener('change', applyFilters);

  // v6.23 — Events overlay toggle
  const eventsToggle = document.getElementById('events-overlay-toggle');
  if (eventsToggle) {
    eventsToggle.addEventListener('change', () => toggleEventsOverlay(eventsToggle.checked));
  }

  // v6.7 — Trade routes toggle (Feature 1)
  const tradeToggle = document.getElementById('trade-routes-toggle');
  if (tradeToggle) {
    tradeToggle.addEventListener('change', () => toggleTradeRoutes(tradeToggle.checked));
  }

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
    // v6.90: re-trigger year-hero + era-ticks sync
    yearSlider.dispatchEvent(new Event('input', { bubbles: true }));
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
    // v6.23 — clear events overlay on reset
    const evToggle = document.getElementById('events-overlay-toggle');
    if (evToggle && evToggle.checked) { evToggle.checked = false; toggleEventsOverlay(false); }
    // v6.7 — also clear trade routes overlay
    const trToggle = document.getElementById('trade-routes-toggle');
    if (trToggle && trToggle.checked) { trToggle.checked = false; toggleTradeRoutes(false); }
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
    // v6.57: audit report 03 flagged 'f' for fullscreen as documented but not wired.
    case 'f':
    case 'F': {
      e.preventDefault();
      const container = document.getElementById('map-container');
      if (container) container.classList.toggle('fullscreen');
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
  const isIt = lang === 'it';
  content.innerHTML = `
    <h2>${isIt ? 'Scorciatoie Tastiera' : 'Keyboard Shortcuts'}</h2>
    <div class="detail-section">
      <div class="section-body">
        <table class="kbd-table">
          <tr><td><kbd>\u2191</kbd> <kbd>\u2193</kbd></td><td>${isIt ? 'Naviga risultati / autocomplete' : 'Navigate results / autocomplete'}</td></tr>
          <tr><td><kbd>Enter</kbd></td><td>${isIt ? 'Apri entit\u00e0 selezionata' : 'Open selected entity'}</td></tr>
          <tr><td><kbd>Esc</kbd></td><td>${isIt ? 'Chiudi pannello / autocomplete' : 'Close panel / autocomplete'}</td></tr>
          <tr><td><kbd>/</kbd></td><td>${isIt ? 'Focus sulla ricerca' : 'Focus search'}</td></tr>
          <tr><td><kbd>?</kbd></td><td>${isIt ? 'Mostra aiuto' : 'Show help'}</td></tr>
        </table>
        <p style="font-size:0.78em;color:var(--text-muted);margin-top:10px">
          ${isIt ? 'Tasto destro sulla mappa per trovare entit\u00e0 vicine.' : 'Right-click on the map to find nearby entities.'}
        </p>
      </div>
    </div>`;
}

// ─── Utility ──────────────────────────────────────────────────
// v6.46: extracted to static/js/utils.js (fmtY, esc, isReal)

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

// ─── i18n ──────────────────────────────────────────────────────
// v6.46: extracted to static/js/i18n.js (I18N + t + initLang + switchLang + applyLangUI)

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
    if (eventsOverlayEnabled) renderEventsOverlay();
    if (tradeRoutesEnabled) renderTradeRoutes();
    // v6.90: dispatch input event → aggiorna year-hero + era-ticks
    slider.dispatchEvent(new Event('input', { bubbles: true }));
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

    const makeCard = (e) => `
        <div class="compare-card" style="border-top:3px solid ${COLORS[e.status]}">
          <h4>${TYPE_ICONS[e.entity_type] || ''} ${esc(e.name_original)}</h4>
          <div class="compare-stat"><span class="label">${t('type')}</span><span class="value">${e.entity_type}</span></div>
          <div class="compare-stat"><span class="label">${t('period')}</span><span class="value">${fmtY(e.year_start)}\u2013${e.year_end ? fmtY(e.year_end) : t('present')}</span></div>
          <div class="compare-stat"><span class="label">${t('duration')}</span><span class="value">${e.duration_years.toLocaleString()} ${t('years')}</span></div>
          <div class="compare-stat"><span class="label">${t('score')}</span><span class="value">${Math.round(e.confidence_score*100)}%</span></div>
          <div class="compare-stat"><span class="label">Status</span><span class="value"><span class="status-badge ${e.status}">${t(e.status)}</span></span></div>
          <div class="compare-stat"><span class="label">${t('sources')}</span><span class="value">${e.sources_count}</span></div>
          <div class="compare-stat"><span class="label">${t('changes')}</span><span class="value">${e.territory_changes_count}</span></div>
          ${e.capital ? `<div class="compare-stat"><span class="label">${t('capital')}</span><span class="value">${esc(e.capital.name)}</span></div>` : ''}
        </div>`;

    content.innerHTML = `
      <h2>\u2696\ufe0f ${t('compare')}</h2>
      <div class="compare-panel">${makeCard(a)}${makeCard(b)}</div>
      <div class="compare-overlap">
        <div style="font-size:0.78em;color:var(--text-muted);margin-bottom:4px">${t('temporal_overlap')}</div>
        <div class="overlap-value">${cmp.temporal_overlap_years.toLocaleString()} ${t('years')}</div>
        ${cmp.overlap_period ? `<div style="font-size:0.75em;color:var(--text-muted);margin-top:2px">${cmp.overlap_period}</div>` : `<div style="font-size:0.75em;color:var(--text-muted)">${t('no_overlap')}</div>`}
      </div>
      <div class="detail-actions">
        <button class="btn-share" onclick="showDetail(${a.id})">${t('view')} ${esc(a.name_original)}</button>
        <button class="btn-share" onclick="showDetail(${b.id})">${t('view')} ${esc(b.name_original)}</button>
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
// v6.46: extracted to static/js/theme.js (initTheme + toggleTheme + applyTheme)
// isReal() moved to static/js/utils.js

// ─── v6.90 A+ year hero + era label sync ────────────────────────
// Aggiorna #year-hero-display, #year-hero-era-suffix, #era-label nell'header
// quando cambia l'anno sullo slider #year-slider. Nessun impatto su handler
// esistenti — questo è un secondo listener indipendente.
// ETHICS: la label dell'era non proiettarsi gerarchie geografiche — usa la
// stessa nomenclatura periodizzante dei chip sidebar (neutra, multi-culturale).
(function initYearHeroSync() {
  const ERA_BANDS = [
    { from: -4500, to: -3000, key: 'era_prehistoric', fallbackIT: 'Preistoria',        fallbackEN: 'Prehistoric' },
    { from: -3000, to: -1200, key: 'era_bronze',      fallbackIT: 'Età del Bronzo',     fallbackEN: 'Bronze Age' },
    { from: -1200, to:  -500, key: 'era_iron',        fallbackIT: 'Età del Ferro',      fallbackEN: 'Iron Age' },
    { from:  -500, to:   500, key: 'era_classical',   fallbackIT: 'Antichità classica', fallbackEN: 'Classical Antiquity' },
    { from:   500, to:  1000, key: 'era_early_medieval', fallbackIT: 'Alto Medioevo',   fallbackEN: 'Early Medieval' },
    { from:  1000, to:  1453, key: 'era_high_medieval',  fallbackIT: 'Basso Medioevo',  fallbackEN: 'High Medieval' },
    { from:  1453, to:  1789, key: 'era_early_modern',   fallbackIT: 'Prima età moderna', fallbackEN: 'Early Modern' },
    { from:  1789, to:  1914, key: 'era_revolutions',    fallbackIT: 'Rivoluzioni',      fallbackEN: 'Age of Revolutions' },
    { from:  1914, to:  1945, key: 'era_world_wars',     fallbackIT: 'Guerre mondiali',  fallbackEN: 'World Wars' },
    { from:  1945, to:  2025, key: 'era_modern',         fallbackIT: 'Età contemporanea',fallbackEN: 'Modern' },
  ];

  function eraForYear(year) {
    for (let i = ERA_BANDS.length - 1; i >= 0; i--) {
      if (year >= ERA_BANDS[i].from) return ERA_BANDS[i];
    }
    return ERA_BANDS[0];
  }

  function formatYearHero(year) {
    const absYear = Math.abs(year).toLocaleString('en-US').replace(/,/g, '.');
    return { display: absYear, suffix: year < 0 ? 'BCE' : 'CE' };
  }

  function getEraLabel(era) {
    const lang = (window.CURRENT_LANG || document.documentElement.lang || 'it').slice(0, 2);
    if (typeof window.t === 'function') {
      const translated = window.t(era.key);
      if (translated && translated !== era.key) return translated.toUpperCase();
    }
    return (lang === 'en' ? era.fallbackEN : era.fallbackIT).toUpperCase();
  }

  function updateYearHero() {
    const slider = document.getElementById('year-slider');
    if (!slider) return;
    const year = parseInt(slider.value, 10);
    const heroDisplay = document.getElementById('year-hero-display');
    const heroSuffix = document.getElementById('year-hero-era-suffix');
    const eraLabel = document.getElementById('era-label');
    const { display, suffix } = formatYearHero(year);
    if (heroDisplay) heroDisplay.textContent = display;
    if (heroSuffix) heroSuffix.textContent = suffix;
    if (eraLabel) {
      const era = eraForYear(year);
      eraLabel.textContent = getEraLabel(era);
      eraLabel.dataset.eraKey = era.key;
    }
  }

  function wire() {
    const slider = document.getElementById('year-slider');
    if (!slider) return;
    slider.addEventListener('input', updateYearHero);
    slider.addEventListener('change', updateYearHero);
    // Initial + after i18n swap
    updateYearHero();
    // v6.78 data-i18n already applied on init; re-render era-label when lang toggles.
    document.addEventListener('atlaspi:langChanged', updateYearHero);
    const langBtn = document.getElementById('lang-toggle');
    if (langBtn) langBtn.addEventListener('click', () => setTimeout(updateYearHero, 50));
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', wire);
  } else {
    wire();
  }

  // Expose for Phase 2.5 (timeline bar) to call after year-slider programmatic updates
  window.atlasPIUpdateYearHero = updateYearHero;

  // ─── v6.90 A+: era ticks overlay nel timeline bar (spec §4) ──
  // Posiziona label ere lungo lo slider (-4500..2025).
  const YEAR_MIN = -4500;
  const YEAR_MAX = 2025;
  const YEAR_SPAN = YEAR_MAX - YEAR_MIN;

  function yearToPercent(year) {
    return ((year - YEAR_MIN) / YEAR_SPAN) * 100;
  }

  function renderEraTicks() {
    const container = document.getElementById('era-ticks-overlay');
    if (!container) return;
    const slider = document.getElementById('year-slider');
    const currentYear = slider ? parseInt(slider.value, 10) : 1500;
    const currentEra = eraForYear(currentYear);
    // Usa solo le prime lettere dell'era come tick (brevità per non sovrapporre)
    // Ticks subset: non metto tutte 10 (sarebbero troppo dense). Uso 6 principali.
    const TICKS = [
      { y: -3000, label: 'Bronze' },
      { y: -500,  label: 'Classical' },
      { y:  500,  label: 'Medieval' },
      { y: 1453,  label: 'Early Modern' },
      { y: 1789,  label: 'Revolutions' },
      { y: 1914,  label: 'Modern' },
    ];
    // Translate labels via window.t if i18n keys exist
    const html = TICKS.map(tick => {
      const pct = yearToPercent(tick.y);
      const bandForTick = eraForYear(tick.y);
      const isActive = bandForTick.key === currentEra.key;
      const label = (typeof window.t === 'function' && window.t(bandForTick.key) && window.t(bandForTick.key) !== bandForTick.key)
        ? window.t(bandForTick.key)
        : tick.label;
      return `<span class="era-tick${isActive ? ' era-tick--active' : ''}" style="left:${pct}%">${label}</span>`;
    }).join('');
    container.innerHTML = html;
  }

  function updateYearDisplayEra() {
    const slider = document.getElementById('year-slider');
    if (!slider) return;
    const y = parseInt(slider.value, 10);
    const displayEra = document.getElementById('year-display-era');
    if (displayEra) displayEra.textContent = y < 0 ? 'BCE' : 'CE';
  }

  // Wire era ticks to slider + initial render
  function wireEraTicks() {
    const slider = document.getElementById('year-slider');
    if (!slider) return;
    renderEraTicks();
    updateYearDisplayEra();
    slider.addEventListener('input', () => {
      renderEraTicks();
      updateYearDisplayEra();
    });
    document.addEventListener('atlaspi:langChanged', renderEraTicks);
    const langBtn = document.getElementById('lang-toggle');
    if (langBtn) langBtn.addEventListener('click', () => setTimeout(renderEraTicks, 50));
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', wireEraTicks);
  } else {
    wireEraTicks();
  }
})();
