/* AtlasPI — Interfaccia web con Leaflet */

const API_BASE = '';
const STATUS_COLORS = {
  confirmed: '#2ecc71',
  uncertain: '#f39c12',
  disputed: '#e74c3c',
};

let map;
let layerGroup;
let allEntities = [];
let selectedLayer = null;

// ─── Inizializzazione ──────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  initMap();
  loadEntities();
  bindEvents();
});

function initMap() {
  map = L.map('map', {
    center: [35, 25],
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
    console.error('Errore caricamento entit\u00e0:', err);
    document.getElementById('results-list').innerHTML =
      '<p class="placeholder">Errore di connessione all\'API</p>';
  }
}

async function loadEntityDetail(id) {
  try {
    const res = await fetch(`${API_BASE}/v1/entities/${id}`);
    return await res.json();
  } catch (err) {
    console.error('Errore caricamento dettaglio:', err);
    return null;
  }
}

// ─── Filtri ─────────────────────────────────────────────────────

function getActiveStatuses() {
  const checks = document.querySelectorAll('.checkbox-group input:checked');
  return Array.from(checks).map(c => c.value);
}

function applyFilters() {
  const search = document.getElementById('search-input').value.toLowerCase().trim();
  const year = parseInt(document.getElementById('year-slider').value, 10);
  const statuses = getActiveStatuses();

  const filtered = allEntities.filter(e => {
    // Status filter
    if (!statuses.includes(e.status)) return false;

    // Year filter
    if (e.year_start > year) return false;
    if (e.year_end !== null && e.year_end < year) return false;

    // Search filter
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
    container.innerHTML = '<p class="placeholder">Nessuna entit\u00e0 trovata</p>';
    return;
  }

  container.innerHTML = entities.map(e => `
    <div class="result-card ${e.status}" data-id="${e.id}">
      <div class="name">${escHtml(e.name_original)}</div>
      <div class="meta">
        ${e.entity_type} &middot;
        ${formatYear(e.year_start)}\u2013${e.year_end ? formatYear(e.year_end) : 'oggi'} &middot;
        <span class="status-badge ${e.status}">${e.status}</span>
      </div>
      <div class="score-bar">
        <div class="score-fill" style="width:${e.confidence_score * 100}%;background:${STATUS_COLORS[e.status]}"></div>
      </div>
    </div>
  `).join('');

  container.querySelectorAll('.result-card').forEach(card => {
    card.addEventListener('click', () => showDetail(parseInt(card.dataset.id, 10)));
  });
}

// ─── Rendering mappa ────────────────────────────────────────────

function renderMap(entities) {
  layerGroup.clearLayers();

  entities.forEach(e => {
    if (!e.boundary_geojson) return;

    const color = STATUS_COLORS[e.status] || '#888';

    try {
      const geo = e.boundary_geojson;

      if (geo.type === 'Point') {
        const [lon, lat] = geo.coordinates;
        const marker = L.circleMarker([lat, lon], {
          radius: 7,
          fillColor: color,
          color: '#fff',
          weight: 1,
          fillOpacity: 0.8,
        });
        marker.bindTooltip(e.name_original, { permanent: false, direction: 'top' });
        marker.on('click', () => showDetail(e.id));
        layerGroup.addLayer(marker);
      } else {
        const layer = L.geoJSON(geo, {
          style: {
            fillColor: color,
            fillOpacity: 0.25,
            color: color,
            weight: 2,
          },
        });
        layer.bindTooltip(e.name_original, { sticky: true });
        layer.on('click', () => showDetail(e.id));
        layerGroup.addLayer(layer);
      }
    } catch (err) {
      console.warn(`GeoJSON non valido per ${e.name_original}:`, err);
    }
  });
}

// ─── Pannello dettaglio ─────────────────────────────────────────

async function showDetail(id) {
  const entity = await loadEntityDetail(id);
  if (!entity) return;

  const panel = document.getElementById('detail-panel');
  const content = document.getElementById('detail-content');

  content.innerHTML = `
    <h2>${escHtml(entity.name_original)}</h2>
    <span class="lang-tag">${entity.name_original_lang}</span>
    <span class="status-badge ${entity.status}">${entity.status}</span>

    <div class="detail-section">
      <h3>Informazioni</h3>
      <p><strong>Tipo:</strong> ${entity.entity_type}</p>
      <p><strong>Periodo:</strong> ${formatYear(entity.year_start)} \u2013 ${entity.year_end ? formatYear(entity.year_end) : 'presente'}</p>
      ${entity.capital ? `<p><strong>Capitale:</strong> ${escHtml(entity.capital.name)} (${entity.capital.lat.toFixed(4)}, ${entity.capital.lon.toFixed(4)})</p>` : ''}
    </div>

    <div class="detail-section">
      <h3>Affidabilit\u00e0</h3>
      <div class="confidence-bar">
        <div class="confidence-fill" style="width:${entity.confidence_score * 100}%;background:${STATUS_COLORS[entity.status]}"></div>
      </div>
      <p style="font-size:0.8em;color:var(--text-muted);margin-top:4px">
        Score: ${entity.confidence_score.toFixed(2)} / 1.00
      </p>
    </div>

    ${entity.name_variants.length > 0 ? `
    <div class="detail-section">
      <h3>Nomi e varianti</h3>
      <ul>
        ${entity.name_variants.map(v => `
          <li>
            <strong>${escHtml(v.name)}</strong>
            <span class="lang-tag">${v.lang}</span>
            ${v.period_start !== null ? `<span style="font-size:0.78em;color:var(--text-muted)">${formatYear(v.period_start)}\u2013${v.period_end ? formatYear(v.period_end) : '...'}</span>` : ''}
            ${v.context ? `<br><span style="font-size:0.8em;color:var(--text-muted)">${escHtml(v.context)}</span>` : ''}
          </li>
        `).join('')}
      </ul>
    </div>
    ` : ''}

    ${entity.territory_changes.length > 0 ? `
    <div class="detail-section">
      <h3>Cambiamenti territoriali</h3>
      <ul>
        ${entity.territory_changes.map(tc => `
          <li>
            <span class="change-type ${tc.change_type}">${tc.change_type.replace(/_/g, ' ')}</span>
            <strong>${formatYear(tc.year)}</strong> \u2014 ${escHtml(tc.region)}
            ${tc.description ? `<br><span style="font-size:0.82em">${escHtml(tc.description)}</span>` : ''}
            ${tc.population_affected ? `<br><span style="font-size:0.78em;color:var(--text-muted)">Popolazione colpita: ~${tc.population_affected.toLocaleString('it-IT')}</span>` : ''}
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
            ${escHtml(s.citation)}
            <span class="lang-tag">${s.source_type}</span>
            ${s.url ? `<br><a href="${escHtml(s.url)}" target="_blank" style="font-size:0.8em;color:var(--accent)">${escHtml(s.url)}</a>` : ''}
          </li>
        `).join('')}
      </ul>
    </div>
    ` : ''}

    ${entity.ethical_notes ? `
    <div class="detail-section">
      <h3>Note etiche</h3>
      <div class="ethics-box">${escHtml(entity.ethical_notes)}</div>
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
    } catch (err) {
      // silently skip
    }
  }
}

function closeDetail() {
  document.getElementById('detail-panel').classList.add('hidden');
}

// ─── Event binding ──────────────────────────────────────────────

function bindEvents() {
  document.getElementById('search-btn').addEventListener('click', applyFilters);
  document.getElementById('search-input').addEventListener('keyup', e => {
    if (e.key === 'Enter') applyFilters();
  });

  const yearSlider = document.getElementById('year-slider');
  const yearDisplay = document.getElementById('year-display');
  yearSlider.addEventListener('input', () => {
    yearDisplay.textContent = formatYear(parseInt(yearSlider.value, 10));
  });
  yearSlider.addEventListener('change', applyFilters);

  document.querySelectorAll('.checkbox-group input').forEach(cb => {
    cb.addEventListener('change', applyFilters);
  });

  document.getElementById('reset-btn').addEventListener('click', () => {
    document.getElementById('search-input').value = '';
    yearSlider.value = 1500;
    yearDisplay.textContent = '1500';
    document.querySelectorAll('.checkbox-group input').forEach(cb => { cb.checked = true; });
    applyFilters();
  });

  document.getElementById('close-detail').addEventListener('click', closeDetail);
}

// ─── Utilit\u00e0 ────────────────────────────────────────────────────

function formatYear(y) {
  if (y < 0) return `${Math.abs(y)} a.C.`;
  return String(y);
}

function escHtml(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}
