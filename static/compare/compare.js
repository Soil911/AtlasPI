/**
 * AtlasPI Entity Comparison Tool — v6.18
 *
 * Pure vanilla JS — no external dependencies.
 * Fetches entity data via the API and renders a side-by-side comparison.
 */

(function () {
  'use strict';

  /* ── Constants ─────────────────────────────────── */

  const API = '';  // Same origin
  const ENT_COLORS = ['#58a6ff', '#f85149', '#3fb950', '#bc8cff'];
  const MAX_ENTITIES = 4;
  const TYPE_COLORS = {
    empire: '#f85149', kingdom: '#58a6ff', republic: '#3fb950',
    dynasty: '#bc8cff', caliphate: '#d29922', sultanate: '#e3b341',
    confederation: '#76e3ea', city_state: '#f778ba', colonial: '#ff7b72',
  };

  /* ── State ─────────────────────────────────────── */

  let selected = [];  // [{id, name, type}]
  let acHighlight = -1;
  let acResults = [];
  let searchTimeout = null;

  /* ── DOM refs ──────────────────────────────────── */

  const $input   = document.getElementById('cp-search');
  const $ac      = document.getElementById('cp-autocomplete');
  const $chips   = document.getElementById('cp-chips');
  const $btn     = document.getElementById('cp-compare-btn');
  const $presets = document.getElementById('cp-presets');
  const $results = document.getElementById('cp-results');
  const $loading = document.getElementById('cp-loading');
  const $selector = document.getElementById('cp-selector');

  /* ── Presets (loaded dynamically) ──────────────── */

  const PRESET_QUERIES = [
    { label: 'Roman Empire vs Persian Empire', search: ['Imperium Romanum', 'Achaemenid Empire'] },
    { label: 'British vs Mongol Empire', search: ['British Empire', 'Mongol Empire'] },
    { label: 'Ottoman vs Byzantine', search: ['Ottoman Empire', 'Byzantine Empire'] },
  ];

  /* ── Init ──────────────────────────────────────── */

  function init() {
    $input.addEventListener('input', onSearchInput);
    $input.addEventListener('keydown', onSearchKeydown);
    $input.addEventListener('focus', function () { if (acResults.length) $ac.classList.add('active'); });
    document.addEventListener('click', function (e) {
      if (!$ac.contains(e.target) && e.target !== $input) {
        $ac.classList.remove('active');
      }
    });
    $btn.addEventListener('click', doCompare);
    renderPresets();
    updateBtn();

    // Check URL params
    var params = new URLSearchParams(window.location.search);
    var idsParam = params.get('ids');
    if (idsParam) {
      loadFromIds(idsParam);
    }
  }

  /* ── Search / Autocomplete ─────────────────────── */

  function onSearchInput() {
    var q = $input.value.trim();
    if (q.length < 2) {
      $ac.classList.remove('active');
      acResults = [];
      return;
    }
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(function () { doSearch(q); }, 250);
  }

  function doSearch(q) {
    fetch(API + '/v1/search?q=' + encodeURIComponent(q) + '&limit=8')
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var items = data.results || data;
        acResults = items;
        renderAutocomplete(items);
      })
      .catch(function () {
        acResults = [];
        $ac.classList.remove('active');
      });
  }

  function renderAutocomplete(items) {
    if (!items.length) {
      $ac.classList.remove('active');
      return;
    }
    acHighlight = -1;
    var html = '';
    for (var i = 0; i < items.length; i++) {
      var it = items[i];
      var already = selected.some(function (s) { return s.id === it.id; });
      if (already) continue;
      var years = formatYear(it.year_start) + ' - ' + (it.year_end ? formatYear(it.year_end) : 'present');
      html += '<div class="cp-ac-item" data-idx="' + i + '">'
        + '<span class="cp-ac-item-name">' + esc(it.name_original || it.name) + '</span>'
        + '<span class="cp-ac-item-meta">' + esc(it.entity_type || '') + ' &middot; ' + years + '</span>'
        + '</div>';
    }
    if (!html) {
      $ac.classList.remove('active');
      return;
    }
    $ac.innerHTML = html;
    $ac.classList.add('active');

    var acItems = $ac.querySelectorAll('.cp-ac-item');
    for (var j = 0; j < acItems.length; j++) {
      (function (el, idx) {
        el.addEventListener('click', function () { selectItem(idx); });
      })(acItems[j], parseInt(acItems[j].getAttribute('data-idx')));
    }
  }

  function onSearchKeydown(e) {
    var items = $ac.querySelectorAll('.cp-ac-item');
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      acHighlight = Math.min(acHighlight + 1, items.length - 1);
      highlightAc(items);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      acHighlight = Math.max(acHighlight - 1, 0);
      highlightAc(items);
    } else if (e.key === 'Enter' && acHighlight >= 0) {
      e.preventDefault();
      var idx = parseInt(items[acHighlight].getAttribute('data-idx'));
      selectItem(idx);
    } else if (e.key === 'Escape') {
      $ac.classList.remove('active');
    }
  }

  function highlightAc(items) {
    for (var i = 0; i < items.length; i++) {
      items[i].classList.toggle('highlighted', i === acHighlight);
    }
  }

  function selectItem(idx) {
    if (selected.length >= MAX_ENTITIES) return;
    var item = acResults[idx];
    if (!item || selected.some(function (s) { return s.id === item.id; })) return;
    selected.push({
      id: item.id,
      name: item.name_original || item.name,
      type: item.entity_type || '',
    });
    $input.value = '';
    $ac.classList.remove('active');
    acResults = [];
    renderChips();
    updateBtn();
  }

  function removeSelected(id) {
    selected = selected.filter(function (s) { return s.id !== id; });
    renderChips();
    updateBtn();
  }

  function renderChips() {
    var html = '';
    for (var i = 0; i < selected.length; i++) {
      var s = selected[i];
      html += '<span class="cp-chip" data-idx="' + i + '">'
        + esc(s.name)
        + '<span class="cp-chip-remove" data-id="' + s.id + '">&times;</span>'
        + '</span>';
    }
    $chips.innerHTML = html;

    var removeBtns = $chips.querySelectorAll('.cp-chip-remove');
    for (var j = 0; j < removeBtns.length; j++) {
      (function (el) {
        el.addEventListener('click', function () {
          removeSelected(parseInt(el.getAttribute('data-id')));
        });
      })(removeBtns[j]);
    }
  }

  function updateBtn() {
    $btn.disabled = selected.length < 2;
    $btn.textContent = selected.length < 2
      ? 'Select at least 2 entities'
      : 'Compare ' + selected.length + ' entities';
  }

  /* ── Presets ───────────────────────────────────── */

  function renderPresets() {
    var html = '';
    for (var i = 0; i < PRESET_QUERIES.length; i++) {
      html += '<button class="cp-preset-btn" data-preset="' + i + '">' + PRESET_QUERIES[i].label + '</button>';
    }
    $presets.innerHTML = html;

    var btns = $presets.querySelectorAll('.cp-preset-btn');
    for (var j = 0; j < btns.length; j++) {
      (function (el, idx) {
        el.addEventListener('click', function () { loadPreset(idx); });
      })(btns[j], parseInt(btns[j].getAttribute('data-preset')));
    }
  }

  function loadPreset(idx) {
    var preset = PRESET_QUERIES[idx];
    selected = [];
    renderChips();
    updateBtn();

    // Search for each entity name and select first match
    var promises = preset.search.map(function (name) {
      return fetch(API + '/v1/search?q=' + encodeURIComponent(name) + '&limit=3')
        .then(function (r) { return r.json(); })
        .then(function (data) {
          var items = data.results || data;
          if (items.length) {
            var it = items[0];
            return { id: it.id, name: it.name_original || it.name, type: it.entity_type || '' };
          }
          return null;
        });
    });

    Promise.all(promises).then(function (results) {
      for (var i = 0; i < results.length; i++) {
        if (results[i] && !selected.some(function (s) { return s.id === results[i].id; })) {
          selected.push(results[i]);
        }
      }
      renderChips();
      updateBtn();
      if (selected.length >= 2) doCompare();
    });
  }

  function loadFromIds(idsStr) {
    $loading.classList.add('active');
    fetch(API + '/v1/compare?ids=' + idsStr)
      .then(function (r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      })
      .then(function (data) {
        // Populate selected from response
        selected = data.entities.map(function (e) {
          return { id: e.id, name: e.name_original, type: e.entity_type };
        });
        renderChips();
        updateBtn();
        renderResults(data);
      })
      .catch(function (err) {
        $loading.classList.remove('active');
        alert('Failed to load comparison: ' + err.message);
      });
  }

  /* ── Compare ───────────────────────────────────── */

  function doCompare() {
    if (selected.length < 2) return;
    var ids = selected.map(function (s) { return s.id; }).join(',');

    // Update URL
    var url = window.location.pathname + '?ids=' + ids;
    history.pushState(null, '', url);

    $loading.classList.add('active');
    $results.classList.remove('active');

    fetch(API + '/v1/compare?ids=' + ids)
      .then(function (r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      })
      .then(function (data) {
        renderResults(data);
      })
      .catch(function (err) {
        $loading.classList.remove('active');
        alert('Comparison failed: ' + err.message);
      });
  }

  /* ── Render ────────────────────────────────────── */

  function renderResults(data) {
    $loading.classList.remove('active');
    $results.classList.add('active');

    var idToIdx = {};
    for (var i = 0; i < data.entities.length; i++) {
      idToIdx[data.entities[i].id] = i;
    }

    renderOverviewCards(data.entities, idToIdx);
    renderTimeline(data.entities, idToIdx);
    renderOverlap(data.overlap, data.entities, idToIdx);
    renderEvents(data.events_by_entity, data.common_events, data.entities, idToIdx);
    renderChains(data.chains_by_entity, data.entities, idToIdx);
    renderDataTable(data.entities, idToIdx);

    // Scroll to results
    $results.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function renderOverviewCards(entities, idToIdx) {
    var container = document.getElementById('cp-overview');
    var html = '';
    for (var i = 0; i < entities.length; i++) {
      var e = entities[i];
      html += '<div class="cp-card" data-idx="' + i + '">'
        + '<div class="cp-card-name">' + esc(e.name_original) + '</div>'
        + '<div class="cp-card-english">' + (e.name_english ? esc(e.name_english) : e.name_original_lang) + '</div>'
        + cardRow('Type', '<span style="text-transform:capitalize">' + esc(e.entity_type) + '</span>')
        + cardRow('Lifespan', formatYear(e.year_start) + ' - ' + (e.year_end ? formatYear(e.year_end) : 'present'))
        + cardRow('Duration', e.duration_years.toLocaleString() + ' years')
        + cardRow('Capital', e.capital ? esc(e.capital.name) : 'Unknown')
        + cardRow('Confidence', renderConfidence(e.confidence_score))
        + cardRow('Status', '<span class="cp-badge cp-badge-' + e.status + '">' + e.status + '</span>')
        + cardRow('Sources', e.sources_count)
        + cardRow('Boundary', e.has_boundary ? 'Available (' + (e.boundary_source || 'unknown') + ')' : 'Not available')
        + '</div>';
    }
    container.innerHTML = html;
  }

  function cardRow(label, value) {
    return '<div class="cp-card-row">'
      + '<span class="cp-card-label">' + label + '</span>'
      + '<span class="cp-card-value">' + value + '</span>'
      + '</div>';
  }

  function renderConfidence(score) {
    var pct = Math.round(score * 100);
    var clr = score >= 0.7 ? '#3fb950' : score >= 0.4 ? '#d29922' : '#f85149';
    return '<span class="cp-confidence">'
      + '<span class="cp-confidence-bar"><span class="cp-confidence-fill" style="width:' + pct + '%;background:' + clr + '"></span></span>'
      + '<span>' + score.toFixed(2) + '</span>'
      + '</span>';
  }

  function renderTimeline(entities, idToIdx) {
    var container = document.getElementById('cp-timeline');
    var minYear = Infinity, maxYear = -Infinity;
    for (var i = 0; i < entities.length; i++) {
      if (entities[i].year_start < minYear) minYear = entities[i].year_start;
      var end = entities[i].year_end || 2025;
      if (end > maxYear) maxYear = end;
    }

    var padding = Math.max(50, Math.round((maxYear - minYear) * 0.05));
    minYear -= padding;
    maxYear += padding;
    var range = maxYear - minYear;

    var svgH = 40 + entities.length * 44 + 40;
    var svgW = 800;
    var barH = 28;
    var leftPad = 10;
    var rightPad = 10;
    var usable = svgW - leftPad - rightPad;

    function xPos(year) {
      return leftPad + ((year - minYear) / range) * usable;
    }

    var svg = '<svg class="cp-timeline-svg" viewBox="0 0 ' + svgW + ' ' + svgH + '" xmlns="http://www.w3.org/2000/svg">';

    // Background
    svg += '<rect width="' + svgW + '" height="' + svgH + '" fill="#161b22" rx="12"/>';

    // Year axis
    var tickStep = niceStep(range);
    var firstTick = Math.ceil(minYear / tickStep) * tickStep;
    for (var t = firstTick; t <= maxYear; t += tickStep) {
      var tx = xPos(t);
      svg += '<line x1="' + tx + '" y1="30" x2="' + tx + '" y2="' + (svgH - 10) + '" stroke="#30363d" stroke-width="0.5"/>';
      svg += '<text x="' + tx + '" y="22" fill="#6e7681" font-size="11" text-anchor="middle" font-family="sans-serif">' + formatYear(t) + '</text>';
    }

    // Entity bars
    for (var j = 0; j < entities.length; j++) {
      var e = entities[j];
      var y = 40 + j * 44;
      var x1 = xPos(e.year_start);
      var x2 = xPos(e.year_end || 2025);
      var w = Math.max(x2 - x1, 2);
      var clr = ENT_COLORS[j] || '#8b949e';

      svg += '<rect x="' + x1 + '" y="' + y + '" width="' + w + '" height="' + barH + '" rx="4" fill="' + clr + '" opacity="0.7"/>';
      svg += '<rect x="' + x1 + '" y="' + y + '" width="' + w + '" height="' + barH + '" rx="4" fill="none" stroke="' + clr + '" stroke-width="1.5"/>';

      // Label
      var label = e.name_english || e.name_original;
      if (label.length > 30) label = label.substring(0, 28) + '...';
      var textX = x1 + 6;
      if (w < 100) textX = x2 + 6;
      svg += '<text x="' + textX + '" y="' + (y + barH / 2 + 4) + '" fill="' + (w < 100 ? clr : '#fff') + '" font-size="12" font-weight="600" font-family="sans-serif">' + esc(label) + '</text>';
    }

    svg += '</svg>';
    container.innerHTML = svg;
  }

  function renderOverlap(overlap, entities, idToIdx) {
    var container = document.getElementById('cp-overlap');
    var html = '';

    // Global overlap
    if (overlap.all && overlap.all.years > 0) {
      html += '<div class="cp-overlap-info">'
        + '<div class="cp-overlap-label">All entities coexisted</div>'
        + '<div class="cp-overlap-value">' + overlap.all.years.toLocaleString() + ' years'
        + ' <span style="font-size:14px;color:#8b949e;font-weight:400">(' + formatYear(overlap.all.start) + ' to ' + formatYear(overlap.all.end) + ')</span></div>'
        + '</div>';
    } else if (entities.length === 2) {
      html += '<div class="cp-overlap-info">'
        + '<div class="cp-overlap-label">Temporal overlap</div>'
        + '<div class="cp-overlap-value" style="color:#f85149">No temporal overlap</div>'
        + '</div>';
    }

    // Pairwise (only show if more than 2 entities)
    if (entities.length > 2 && overlap.pairwise) {
      html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:8px">';
      for (var i = 0; i < overlap.pairwise.length; i++) {
        var pw = overlap.pairwise[i];
        var e1 = entities[idToIdx[pw.entity_ids[0]]];
        var e2 = entities[idToIdx[pw.entity_ids[1]]];
        var name1 = shortName(e1.name_english || e1.name_original);
        var name2 = shortName(e2.name_english || e2.name_original);
        html += '<div class="cp-overlap-info" style="margin-bottom:0">'
          + '<div class="cp-overlap-label">' + esc(name1) + ' / ' + esc(name2) + '</div>'
          + '<div class="cp-overlap-value" style="font-size:16px">'
          + (pw.years > 0 ? pw.years.toLocaleString() + ' years' : '<span style="color:#f85149">No overlap</span>')
          + '</div></div>';
      }
      html += '</div>';
    }

    container.innerHTML = html || '<div class="cp-empty">No overlap data available</div>';
  }

  function renderEvents(eventsByEntity, commonEvents, entities, idToIdx) {
    var container = document.getElementById('cp-events');

    // Merge all events into a single timeline, sorted by year
    var allEvents = [];
    for (var i = 0; i < entities.length; i++) {
      var evts = eventsByEntity[String(entities[i].id)] || [];
      for (var j = 0; j < evts.length; j++) {
        allEvents.push({ event: evts[j], entityIdx: i, entityId: entities[i].id });
      }
    }

    // Deduplicate (same event may appear for multiple entities)
    var seenEvents = {};
    var deduped = [];
    for (var k = 0; k < allEvents.length; k++) {
      var key = allEvents[k].event.id;
      if (!seenEvents[key]) {
        seenEvents[key] = { event: allEvents[k].event, entities: [allEvents[k].entityIdx] };
        deduped.push(seenEvents[key]);
      } else {
        seenEvents[key].entities.push(allEvents[k].entityIdx);
      }
    }

    deduped.sort(function (a, b) { return a.event.year - b.event.year; });

    if (!deduped.length) {
      container.innerHTML = '<div class="cp-empty">No events linked to these entities</div>';
      return;
    }

    var html = '<div class="cp-events-container">';
    for (var m = 0; m < deduped.length; m++) {
      var ev = deduped[m].event;
      var entIdxs = deduped[m].entities;
      var dotColor = ENT_COLORS[entIdxs[0]] || '#8b949e';
      var shared = entIdxs.length > 1;

      html += '<div class="cp-event-item">'
        + '<span class="cp-event-dot" style="background:' + dotColor + '"></span>'
        + '<span class="cp-event-year">' + formatYear(ev.year) + '</span>'
        + '<span>'
        + '<span class="cp-event-name">' + esc(ev.name_original) + '</span>'
        + '<span class="cp-event-type">' + esc(ev.event_type) + '</span>'
        + (shared ? '<span class="cp-event-shared">shared</span>' : '')
        + '</span>'
        + '</div>';
    }
    html += '</div>';

    container.innerHTML = html;
  }

  function renderChains(chainsByEntity, entities, idToIdx) {
    var container = document.getElementById('cp-chains');

    // Collect unique chains
    var seen = {};
    var allChains = [];
    for (var i = 0; i < entities.length; i++) {
      var chains = chainsByEntity[String(entities[i].id)] || [];
      for (var j = 0; j < chains.length; j++) {
        if (!seen[chains[j].chain_id]) {
          seen[chains[j].chain_id] = true;
          allChains.push(chains[j]);
        }
      }
    }

    if (!allChains.length) {
      container.innerHTML = '<div class="cp-empty">No dynasty chains involve these entities</div>';
      return;
    }

    var html = '';
    for (var k = 0; k < allChains.length; k++) {
      var c = allChains[k];
      html += '<div class="cp-chain-row">'
        + '<div class="cp-chain-name">' + esc(c.chain_name) + '</div>'
        + '<div class="cp-chain-meta">' + esc(c.chain_type) + (c.region ? ' &middot; ' + esc(c.region) : '') + '</div>'
        + '<div class="cp-chain-links">';

      for (var l = 0; l < c.links.length; l++) {
        var lk = c.links[l];
        if (l > 0) {
          var violent = lk.is_violent;
          html += '<span class="cp-chain-arrow' + (violent ? ' violent' : '') + '">'
            + (violent ? '&#9876;' : '&#8594;') + '</span>';
        }

        var cmpIdx = -1;
        if (lk.is_compared) {
          // Find which compared entity this is
          for (var n = 0; n < entities.length; n++) {
            if (entities[n].id === lk.entity_id) { cmpIdx = n; break; }
          }
        }

        html += '<span class="cp-chain-link' + (lk.is_compared ? ' compared' : '') + '"'
          + (cmpIdx >= 0 ? ' data-cmp-idx="' + cmpIdx + '"' : '')
          + '>' + esc(lk.entity_name || 'Unknown') + '</span>';
      }

      html += '</div></div>';
    }

    container.innerHTML = html;
  }

  function renderDataTable(entities, idToIdx) {
    var container = document.getElementById('cp-table');

    var fields = [
      { key: 'name_original', label: 'Name (original)' },
      { key: 'name_english', label: 'Name (English)' },
      { key: 'entity_type', label: 'Type' },
      { key: 'year_start', label: 'Year start', fmt: formatYear },
      { key: 'year_end', label: 'Year end', fmt: function (v) { return v ? formatYear(v) : 'present'; } },
      { key: 'duration_years', label: 'Duration (years)', fmt: function (v) { return v.toLocaleString(); } },
      { key: 'capital', label: 'Capital', fmt: function (v) { return v ? v.name : 'Unknown'; } },
      { key: 'confidence_score', label: 'Confidence', fmt: function (v) { return v.toFixed(2); } },
      { key: 'status', label: 'Status' },
      { key: 'has_boundary', label: 'Boundary', fmt: function (v) { return v ? 'Yes' : 'No'; } },
      { key: 'boundary_source', label: 'Boundary source', fmt: function (v) { return v || '-'; } },
      { key: 'sources_count', label: 'Sources' },
      { key: 'name_variants_count', label: 'Name variants' },
      { key: 'territory_changes_count', label: 'Territory changes' },
    ];

    var html = '<div class="cp-table-wrap"><table class="cp-table">';

    // Header
    html += '<thead><tr><th>Field</th>';
    for (var i = 0; i < entities.length; i++) {
      html += '<th style="color:' + ENT_COLORS[i] + '">' + esc(shortName(entities[i].name_original)) + '</th>';
    }
    html += '</tr></thead><tbody>';

    // Rows
    for (var j = 0; j < fields.length; j++) {
      var f = fields[j];
      var vals = entities.map(function (e) {
        var v = e[f.key];
        return f.fmt ? f.fmt(v) : (v != null ? String(v) : '-');
      });

      // Check if values differ
      var allSame = vals.every(function (v) { return v === vals[0]; });
      var rowCls = allSame ? '' : ' class="diff"';

      html += '<tr' + rowCls + '><td>' + f.label + '</td>';
      for (var k = 0; k < vals.length; k++) {
        html += '<td>' + esc(String(vals[k])) + '</td>';
      }
      html += '</tr>';
    }

    html += '</tbody></table></div>';
    container.innerHTML = html;
  }

  /* ── Helpers ───────────────────────────────────── */

  function formatYear(y) {
    if (y == null) return '?';
    if (y < 0) return Math.abs(y) + ' BCE';
    if (y === 0) return '1 BCE';
    return y + ' CE';
  }

  function shortName(name) {
    return name.length > 25 ? name.substring(0, 23) + '...' : name;
  }

  function esc(s) {
    if (s == null) return '';
    var d = document.createElement('div');
    d.appendChild(document.createTextNode(String(s)));
    return d.innerHTML;
  }

  function niceStep(range) {
    if (range <= 100) return 10;
    if (range <= 500) return 50;
    if (range <= 1000) return 100;
    if (range <= 2000) return 200;
    if (range <= 5000) return 500;
    return 1000;
  }

  /* ── Boot ──────────────────────────────────────── */

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
