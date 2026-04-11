/* AtlasPI — Interfaccia web con Leaflet */

const API_BASE = '';
const STATUS_COLORS = {
  confirmed: '#3fb950',
  uncertain: '#d29922',
  disputed: '#f85149',
};

let map;
let layerGroup;
let allEntities = [];

// ─── Inizializzazione ──────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  initMap();
  loadEntities();
  bindEvents();
});

function initMap() {
  map = L.map('map', {
    center: [30, 20],
    zoom: 3,
    minZoom: 2,
    maxZoom: 12,
    zoomControl: true,
  });

  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 19,
  }).addTo(map);

  layerGroup = L.layerGroup().addTo(map);
}

// ─── API ────────────────────────────────────────────────────────

async function loadEntities() {
  try {
    const res = await fetch(`${API_BASE}/v1/entities`);
    const data = await res.json();
    allEntities = data.entities;
    document.getElementById('entity-count').textContent = `${data.count} entit\u00e0`;
    applyFilters();
  } catch (err) {
    console.error('Errore caricamento:', err);
    document.getElementById('results-list').innerHTML =
      '<p class="placeholder">Errore di connessione all\'API</p>';
  }
}

async function loadEntityDetail(id) {
  try {
    const res = await fetch(`${API_BASE}/v1/entities/${id}`);
    return await res.json();
  } catch (err) {
    console.error('Errore dettaglio:', err);
    return null;
  }
}

// ─── Filtri ─────────────────────────────────────────────────────

function getActiveStatuses() {
  return Array.from(document.querySelectorAll('.checkbox-group input:checked')).map(c => c.value);
}

function applyFilters() {
  const search = document.getElementById('search-input').value.toLowerCase().trim();
  const year = parseInt(document.getElementById('year-slider').value, 10);
  const statuses = getActiveStatuses();

  const filtered = allEntities.filter(e => {
    if (!statuses.includes(e.status)) return false;
    if (e.year_start > year) return false;
    if (e.year_end !== null && e.year_end < year) return false;

    if (search) {
      const inOriginal = e.name_original.toLowerCase().includes(search);
      const inVariants = (e.name_variants || []).some(v =>
        v.name.toLowerCase().includes(search)
      );
      if (!inOriginal && !inVariants) return false;
    }

    return true;
  });

  renderResults(filtered);
  renderMap(filtered);
}

// ─── Rendering lista ────────────────────────────────────────────

function renderResults(entities) {
  const container = document.getElementById('results-list');

  if (entities.length === 0) {
    container.innerHTML = '<p class="placeholder">Nessuna entit\u00e0 trovata per i filtri selezionati</p>';
    return;
  }

  container.innerHTML = entities.map(e => {
    const scorePercent = Math.round(e.confidence_score * 100);
    return `
    <div class="result-card ${e.status}" data-id="${e.id}">
      <div class="name">
        ${esc(e.name_original)}
        ${hasRealBoundary(e) ? '' : '<span class="precision-tag approx" title="Confini approssimativi">~</span>'}
      </div>
      <div class="meta">
        ${e.entity_type} &middot;
        ${fmtYear(e.year_start)}\u2013${e.year_end ? fmtYear(e.year_end) : 'oggi'} &middot;
        <span class="status-badge ${e.status}">${e.status}</span>
        &middot; ${scorePercent}%
      </div>
      <div class="score-bar">
        <div class="score-fill" style="width:${scorePercent}%;background:${STATUS_COLORS[e.status]}"></div>
      </div>
    </div>`;
  }).join('');

  container.querySelectorAll('.result-card').forEach(card => {
    card.addEventListener('click', () => showDetail(parseInt(card.dataset.id, 10)));
  });
}

// ─── Rendering mappa ────────────────────────────────────────────

function renderMap(entities) {
  layerGroup.clearLayers();

  entities.forEach(e => {
    if (!e.boundary_geojson) return;
    const color = STATUS_COLORS[e.status] || '#8b949e';

    try {
      const geo = e.boundary_geojson;

      if (geo.type === 'Point') {
        const [lon, lat] = geo.coordinates;
        const marker = L.circleMarker([lat, lon], {
          radius: 8,
          fillColor: color,
          color: '#fff',
          weight: 1.5,
          fillOpacity: 0.85,
        });
        marker.bindTooltip(tooltipContent(e), { direction: 'top', className: '' });
        marker.on('click', () => showDetail(e.id));
        layerGroup.addLayer(marker);
      } else {
        const isReal = hasRealBoundary(e);
        const layer = L.geoJSON(geo, {
          style: {
            fillColor: color,
            fillOpacity: isReal ? 0.18 : 0.10,
            color: color,
            weight: isReal ? 2 : 1.5,
            dashArray: e.status === 'disputed' ? '6,4' : (isReal ? null : '4,3'),
            opacity: isReal ? 0.8 : 0.5,
          },
        });
        layer.bindTooltip(tooltipContent(e), { sticky: true, className: '' });
        layer.on('click', () => showDetail(e.id));
        layerGroup.addLayer(layer);

        // Etichetta al centro del poligono
        const center = layer.getBounds().getCenter();
        const label = L.marker(center, {
          icon: L.divIcon({
            className: '',
            html: `<div style="
              color:${color};
              font-size:11px;
              font-weight:600;
              text-shadow:0 0 4px rgba(0,0,0,0.8),0 0 2px rgba(0,0,0,0.9);
              white-space:nowrap;
              pointer-events:none;
            ">${esc(e.name_original)}</div>`,
            iconSize: null,
            iconAnchor: [0, 0],
          }),
          interactive: false,
        });
        layerGroup.addLayer(label);
      }
    } catch (err) {
      console.warn(`GeoJSON error for ${e.name_original}:`, err);
    }
  });
}

function tooltipContent(e) {
  const score = Math.round(e.confidence_score * 100);
  return `<strong>${esc(e.name_original)}</strong><br>
    ${e.entity_type} &middot; ${fmtYear(e.year_start)}\u2013${e.year_end ? fmtYear(e.year_end) : 'oggi'}<br>
    Affidabilit\u00e0: ${score}% &middot; <em>${e.status}</em>`;
}

// ─── Pannello dettaglio ─────────────────────────────────────────

async function showDetail(id) {
  const entity = await loadEntityDetail(id);
  if (!entity) return;

  // Nascondi info overlay
  const info = document.getElementById('map-info');
  if (info) info.style.display = 'none';

  const panel = document.getElementById('detail-panel');
  const content = document.getElementById('detail-content');

  const scorePercent = Math.round(entity.confidence_score * 100);
  const scoreColor = STATUS_COLORS[entity.status] || '#8b949e';

  content.innerHTML = `
    <h2>${esc(entity.name_original)}</h2>
    <span class="lang-tag">${entity.name_original_lang}</span>
    <span class="status-badge ${entity.status}">${entity.status}</span>

    <div class="detail-section">
      <h3>Informazioni</h3>
      <p><strong>Tipo:</strong> ${entity.entity_type}</p>
      <p><strong>Periodo:</strong> ${fmtYear(entity.year_start)} \u2013 ${entity.year_end ? fmtYear(entity.year_end) : 'presente'}</p>
      ${entity.capital ? `<p><strong>Capitale:</strong> ${esc(entity.capital.name)} (${entity.capital.lat.toFixed(4)}, ${entity.capital.lon.toFixed(4)})</p>` : ''}
    </div>

    <div class="detail-section">
      <h3>Affidabilit\u00e0 dei dati</h3>
      <div class="confidence-bar">
        <div class="confidence-fill" style="width:${scorePercent}%;background:${scoreColor}"></div>
      </div>
      <p style="font-size:0.78em;color:var(--text-muted);margin-top:4px">
        Confidence score: ${entity.confidence_score.toFixed(2)} / 1.00
        ${entity.confidence_score < 0.6 ? ' \u2014 <span style="color:var(--uncertain)">dati parziali o incerti</span>' : ''}
      </p>
      ${entity.boundary_geojson ? (hasRealBoundary(entity) ? `
        <div class="boundary-notice" style="border-color:rgba(63,185,80,0.3);background:rgba(63,185,80,0.08);color:var(--confirmed)">
          Confini estratti da dataset accademici. Verificare le fonti
          per dettagli sulla precisione e il periodo di riferimento.
        </div>
      ` : `
        <div class="boundary-notice">
          I confini mostrati sono approssimazioni geometriche a scopo
          dimostrativo. Per confini storici verificati, consultare le fonti
          accademiche elencate sotto.
        </div>
      `) : ''}
    </div>

    ${entity.name_variants.length > 0 ? `
    <div class="detail-section">
      <h3>Nomi e varianti (ETHICS-001)</h3>
      <ul>
        ${entity.name_variants.map(v => `
          <li>
            <strong>${esc(v.name)}</strong>
            <span class="lang-tag">${v.lang}</span>
            ${v.period_start !== null ? `<span style="font-size:0.75em;color:var(--text-muted)">${fmtYear(v.period_start)}\u2013${v.period_end ? fmtYear(v.period_end) : '...'}</span>` : ''}
            ${v.context ? `<br><span style="font-size:0.78em;color:var(--text-muted)">${esc(v.context)}</span>` : ''}
            ${v.source ? `<br><span style="font-size:0.7em;color:var(--accent)">Fonte: ${esc(v.source)}</span>` : ''}
          </li>
        `).join('')}
      </ul>
    </div>
    ` : ''}

    ${entity.territory_changes.length > 0 ? `
    <div class="detail-section">
      <h3>Cambiamenti territoriali (ETHICS-002)</h3>
      <ul>
        ${entity.territory_changes.map(tc => `
          <li>
            <span class="change-type ${tc.change_type}">${tc.change_type.replace(/_/g, ' ')}</span>
            <strong>${fmtYear(tc.year)}</strong> \u2014 ${esc(tc.region)}
            <span style="font-size:0.7em;color:var(--text-muted)">(${Math.round(tc.confidence_score*100)}%)</span>
            ${tc.description ? `<br><span style="font-size:0.8em">${esc(tc.description)}</span>` : ''}
            ${tc.population_affected ? `<br><span style="font-size:0.75em;color:var(--uncertain)">Popolazione colpita: ~${tc.population_affected.toLocaleString('it-IT')}</span>` : ''}
          </li>
        `).join('')}
      </ul>
    </div>
    ` : ''}

    ${entity.sources.length > 0 ? `
    <div class="detail-section">
      <h3>Fonti</h3>
      <ul>
        ${entity.sources.map(s => `
          <li>
            ${esc(s.citation)}
            <span class="lang-tag">${s.source_type}</span>
            ${s.url ? `<br><a href="${esc(s.url)}" target="_blank" rel="noopener" style="font-size:0.78em;color:var(--accent)">${esc(s.url)}</a>` : ''}
          </li>
        `).join('')}
      </ul>
    </div>
    ` : ''}

    ${entity.ethical_notes ? `
    <div class="detail-section">
      <h3>Governance etica</h3>
      <div class="ethics-box">${esc(entity.ethical_notes)}</div>
    </div>
    ` : ''}
  `;

  panel.classList.remove('hidden');

  // Zoom sulla mappa
  if (entity.boundary_geojson) {
    try {
      if (entity.boundary_geojson.type === 'Point') {
        const [lon, lat] = entity.boundary_geojson.coordinates;
        map.setView([lat, lon], 6, { animate: true });
      } else {
        const tempLayer = L.geoJSON(entity.boundary_geojson);
        map.fitBounds(tempLayer.getBounds(), { padding: [50, 50], animate: true });
      }
    } catch (_) { /* skip */ }
  }
}

function closeDetail() {
  document.getElementById('detail-panel').classList.add('hidden');
  const info = document.getElementById('map-info');
  if (info) info.style.display = '';
}

// ─── Event binding ──────────────────────────────────────────────

function bindEvents() {
  document.getElementById('search-btn').addEventListener('click', applyFilters);
  document.getElementById('search-input').addEventListener('keyup', e => {
    if (e.key === 'Enter') applyFilters();
  });
  // Live search while typing
  document.getElementById('search-input').addEventListener('input', applyFilters);

  const yearSlider = document.getElementById('year-slider');
  const yearDisplay = document.getElementById('year-display');
  yearSlider.addEventListener('input', () => {
    yearDisplay.textContent = fmtYear(parseInt(yearSlider.value, 10));
    applyFilters();
  });

  document.querySelectorAll('.checkbox-group input').forEach(cb => {
    cb.addEventListener('change', applyFilters);
  });

  document.getElementById('reset-btn').addEventListener('click', () => {
    document.getElementById('search-input').value = '';
    yearSlider.value = 1500;
    yearDisplay.textContent = '1500';
    document.querySelectorAll('.checkbox-group input').forEach(cb => { cb.checked = true; });
    applyFilters();
    closeDetail();
  });

  document.getElementById('close-detail').addEventListener('click', closeDetail);
}

// ─── Utility ────────────────────────────────────────────────────

function fmtYear(y) {
  if (y < 0) return `${Math.abs(y)} a.C.`;
  return String(y);
}

function esc(str) {
  if (!str) return '';
  const d = document.createElement('div');
  d.textContent = str;
  return d.innerHTML;
}

function hasRealBoundary(e) {
  if (!e.boundary_geojson) return false;
  // Real boundaries from academic sources have many more points
  // than our hand-drawn approximations (typically >50 vs <30)
  const geo = e.boundary_geojson;
  let pts = 0;
  if (geo.type === 'Polygon') {
    pts = geo.coordinates.reduce((sum, ring) => sum + ring.length, 0);
  } else if (geo.type === 'MultiPolygon') {
    pts = geo.coordinates.reduce((sum, poly) =>
      sum + poly.reduce((s, ring) => s + ring.length, 0), 0);
  }
  return pts > 50;
}
