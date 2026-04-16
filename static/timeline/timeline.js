/**
 * AtlasPI Interactive Timeline — v6.17
 *
 * Pure SVG timeline renderer. No external dependencies.
 * Handles 850+ entities, 297+ events, 21 dynasty chains.
 * Supports negative years (BCE), zoom, pan, search, touch.
 */

(function () {
  'use strict';

  // ── Constants ──────────────────────────────────────────────────
  const MIN_YEAR = -5000;
  const MAX_YEAR = 2050;
  const ENTITY_BAR_HEIGHT = 6;
  const ENTITY_GAP = 2;
  const EVENT_MARKER_R = 5;
  const AXIS_HEIGHT = 40;
  const CHAIN_LINK_R = 4;

  const TYPE_COLORS = {
    empire: '#f85149',
    kingdom: '#58a6ff',
    republic: '#3fb950',
    dynasty: '#bc8cff',
    caliphate: '#d29922',
    sultanate: '#e3b341',
    confederation: '#76e3ea',
    city_state: '#f778ba',
    colonial_territory: '#ff7b72',
    tribal_confederation: '#76e3ea',
    khanate: '#d29922',
    principality: '#bc8cff',
    shogunate: '#e3b341',
    viceroyalty: '#ff7b72',
    theocracy: '#f778ba',
    protectorate: '#ff7b72',
    mandate: '#ff7b72',
    other: '#8b949e',
  };

  const EVENT_SHAPES = {
    BATTLE: '\u2694',          // crossed swords
    SIEGE: '\u26F0',           // mountain (fortification)
    TREATY: '\u270B',          // hand
    REBELLION: '\u2607',       // lightning
    REVOLUTION: '\u2605',      // star
    CORONATION: '\u265B',      // crown
    DEATH_OF_RULER: '\u2020',  // dagger
    CONQUEST: '\u2694',
    FOUNDING_CITY: '\u2302',   // house
    FOUNDING_STATE: '\u2691',  // flag
    DISSOLUTION_STATE: '\u2612', // x-box
    GENOCIDE: '\u26A0',        // warning
    COLONIAL_VIOLENCE: '\u26A0',
    MASSACRE: '\u26A0',
    EPIDEMIC: '\u2623',        // biohazard
    EARTHQUAKE: '\u2248',      // approx
    VOLCANIC_ERUPTION: '\u25B2', // triangle
    EXPLORATION: '\u2690',     // flag
    TRADE_AGREEMENT: '\u2696', // scales
    RELIGIOUS_EVENT: '\u2721', // star
    TECHNOLOGICAL_EVENT: '\u2699', // gear
    OTHER: '\u25CF',           // circle
  };

  // ── State ──────────────────────────────────────────────────────
  let data = { entities: [], events: [], chains: [] };
  let viewStart = -3000;
  let viewEnd = 2024;
  let panX = 0;
  let isDragging = false;
  let dragStartX = 0;
  let dragStartPan = 0;
  let scrollY = 0;
  let maxScroll = 0;

  // Touch state
  let lastTouchDist = 0;
  let lastTouchX = 0;

  // Layers
  let showEntities = true;
  let showEvents = true;
  let showChains = true;

  // Search
  let searchTerm = '';

  // Canvas dimensions
  let W = 0;
  let H = 0;

  // DOM refs
  let svg, tooltip, statusLeft, statusRight, loadingEl, mainEl;

  // ── Helpers ────────────────────────────────────────────────────

  function yearToX(year) {
    const span = viewEnd - viewStart;
    if (span <= 0) return 0;
    return ((year - viewStart) / span) * W;
  }

  function xToYear(x) {
    const span = viewEnd - viewStart;
    return viewStart + (x / W) * span;
  }

  function formatYear(y) {
    if (y < 0) return Math.abs(y) + ' BCE';
    if (y === 0) return '1 BCE';
    return y + ' CE';
  }

  function typeColor(t) {
    const key = (t || 'other').toLowerCase().replace(/ /g, '_');
    return TYPE_COLORS[key] || TYPE_COLORS.other;
  }

  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

  function escHtml(s) {
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  function matchesSearch(name) {
    if (!searchTerm) return true;
    return name.toLowerCase().includes(searchTerm);
  }

  // ── SVG helpers ────────────────────────────────────────────────

  function svgEl(tag, attrs) {
    const el = document.createElementNS('http://www.w3.org/2000/svg', tag);
    if (attrs) {
      for (const k in attrs) {
        el.setAttribute(k, attrs[k]);
      }
    }
    return el;
  }

  function clearSvg() {
    while (svg.firstChild) svg.removeChild(svg.firstChild);
  }

  // ── Data Loading ──────────────────────────────────────────────

  async function loadData() {
    const CACHE_KEY = 'atlaspi_timeline_data';
    const CACHE_TS_KEY = 'atlaspi_timeline_ts';
    const CACHE_TTL = 30 * 60 * 1000; // 30 min

    // Try localStorage cache
    try {
      const ts = localStorage.getItem(CACHE_TS_KEY);
      if (ts && Date.now() - parseInt(ts, 10) < CACHE_TTL) {
        const cached = localStorage.getItem(CACHE_KEY);
        if (cached) {
          data = JSON.parse(cached);
          return;
        }
      }
    } catch (_) { /* ignore */ }

    // Fetch from API
    const res = await fetch('/v1/timeline-data');
    if (!res.ok) throw new Error('Failed to load timeline data: ' + res.status);
    data = await res.json();

    // Cache
    try {
      localStorage.setItem(CACHE_KEY, JSON.stringify(data));
      localStorage.setItem(CACHE_TS_KEY, String(Date.now()));
    } catch (_) { /* quota exceeded — ignore */ }
  }

  // ── Rendering ─────────────────────────────────────────────────

  function render() {
    clearSvg();

    svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    svg.setAttribute('width', W);
    svg.setAttribute('height', H);

    const contentTop = AXIS_HEIGHT;
    const contentH = H - AXIS_HEIGHT;

    // Background
    const bg = svgEl('rect', { x:0, y:0, width:W, height:H, fill:'#0d1117' });
    svg.appendChild(bg);

    // Clip for content area
    const defs = svgEl('defs');
    const clipPath = svgEl('clipPath', { id: 'content-clip' });
    clipPath.appendChild(svgEl('rect', { x:0, y:contentTop, width:W, height:contentH }));
    defs.appendChild(clipPath);
    svg.appendChild(defs);

    // Content group (scrollable)
    const contentGroup = svgEl('g', { 'clip-path': 'url(#content-clip)' });
    const scrollGroup = svgEl('g', { transform: 'translate(0,' + (-scrollY) + ')' });
    contentGroup.appendChild(scrollGroup);

    let yOffset = contentTop + 10;

    // ── Entities layer ──
    if (showEntities && data.entities.length) {
      yOffset = renderEntities(scrollGroup, yOffset);
    }

    // ── Chains layer ──
    if (showChains && data.chains.length) {
      yOffset = renderChains(scrollGroup, yOffset);
    }

    svg.appendChild(contentGroup);

    // ── Events layer (drawn on top, not scrolled with content for visibility) ──
    if (showEvents && data.events.length) {
      const evGroup = svgEl('g', { 'clip-path': 'url(#content-clip)' });
      renderEvents(evGroup, contentTop, contentH);
      svg.appendChild(evGroup);
    }

    // Track max scroll
    maxScroll = Math.max(0, yOffset - H + 40);

    // ── Time axis (always on top) ──
    renderAxis();

    // Status bar update
    updateStatus();
  }

  function renderAxis() {
    const axisGroup = svgEl('g');

    // Background bar
    axisGroup.appendChild(svgEl('rect', {
      x: 0, y: 0, width: W, height: AXIS_HEIGHT,
      fill: '#161b22',
    }));

    // Bottom line
    axisGroup.appendChild(svgEl('line', {
      x1: 0, y1: AXIS_HEIGHT, x2: W, y2: AXIS_HEIGHT,
      stroke: '#30363d', 'stroke-width': 1,
    }));

    // Tick marks
    const span = viewEnd - viewStart;
    let step;
    if (span > 4000) step = 1000;
    else if (span > 2000) step = 500;
    else if (span > 800) step = 200;
    else if (span > 400) step = 100;
    else if (span > 150) step = 50;
    else if (span > 60) step = 20;
    else if (span > 25) step = 10;
    else if (span > 10) step = 5;
    else step = 1;

    const firstTick = Math.ceil(viewStart / step) * step;
    for (let year = firstTick; year <= viewEnd; year += step) {
      const x = yearToX(year);
      if (x < 0 || x > W) continue;

      // Tick line
      axisGroup.appendChild(svgEl('line', {
        x1: x, y1: AXIS_HEIGHT - 8, x2: x, y2: AXIS_HEIGHT,
        stroke: '#484f58', 'stroke-width': 1,
      }));

      // Gridline
      axisGroup.appendChild(svgEl('line', {
        x1: x, y1: AXIS_HEIGHT, x2: x, y2: H,
        stroke: '#21262d', 'stroke-width': 0.5,
      }));

      // Label
      const label = svgEl('text', {
        x: x, y: AXIS_HEIGHT - 14,
        'text-anchor': 'middle',
        fill: '#8b949e',
        'font-size': '11',
        'font-family': "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      });
      label.textContent = formatYear(year);
      axisGroup.appendChild(label);
    }

    svg.appendChild(axisGroup);
  }

  function renderEntities(parent, yStart) {
    let y = yStart;
    const visibleEntities = data.entities.filter(function (e) {
      const x1 = yearToX(e.year_start);
      const x2 = yearToX(e.year_end || MAX_YEAR);
      if (x2 < 0 || x1 > W) return false;
      return matchesSearch(e.name);
    });

    // Sort by start year, then by span length (longer first)
    visibleEntities.sort(function (a, b) {
      if (a.year_start !== b.year_start) return a.year_start - b.year_start;
      return (b.year_end || MAX_YEAR) - (a.year_end || MAX_YEAR);
    });

    // Simple row packing to avoid overlaps
    var rows = [];

    for (var i = 0; i < visibleEntities.length; i++) {
      var e = visibleEntities[i];
      var x1 = Math.max(0, yearToX(e.year_start));
      var x2 = Math.min(W, yearToX(e.year_end || MAX_YEAR));
      var barW = Math.max(2, x2 - x1);

      // Find row where this bar fits
      var placed = false;
      for (var r = 0; r < rows.length; r++) {
        if (rows[r] <= x1) {
          rows[r] = x1 + barW + 2;
          renderEntityBar(parent, e, x1, y + r * (ENTITY_BAR_HEIGHT + ENTITY_GAP), barW);
          placed = true;
          break;
        }
      }
      if (!placed) {
        rows.push(x1 + barW + 2);
        renderEntityBar(parent, e, x1, y + rows.length * (ENTITY_BAR_HEIGHT + ENTITY_GAP) - (ENTITY_BAR_HEIGHT + ENTITY_GAP), barW);
      }
    }

    return y + Math.max(rows.length, 1) * (ENTITY_BAR_HEIGHT + ENTITY_GAP) + 20;
  }

  function renderEntityBar(parent, e, x, y, w) {
    var color = typeColor(e.type);
    var opacity = searchTerm && !matchesSearch(e.name) ? 0.15 : (0.5 + e.confidence * 0.5);

    var rect = svgEl('rect', {
      x: x, y: y, width: w, height: ENTITY_BAR_HEIGHT,
      rx: 2, ry: 2,
      fill: color,
      opacity: opacity,
      'data-entity-id': e.id,
    });
    rect.style.cursor = 'pointer';
    rect.style.transition = 'opacity .15s';

    rect.addEventListener('mouseenter', function (ev) {
      rect.setAttribute('opacity', '1');
      showTooltip(ev, entityTooltip(e));
    });
    rect.addEventListener('mouseleave', function () {
      rect.setAttribute('opacity', String(opacity));
      hideTooltip();
    });
    rect.addEventListener('click', function () {
      window.open('/v1/entity/' + e.id, '_blank');
    });

    // Label if bar is wide enough
    if (w > 50) {
      var fontSize = Math.min(10, ENTITY_BAR_HEIGHT + 3);
      var label = svgEl('text', {
        x: x + 4, y: y + ENTITY_BAR_HEIGHT - 1,
        fill: '#e6edf3',
        'font-size': fontSize,
        'font-family': "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        'pointer-events': 'none',
      });
      // Truncate name to fit
      var maxChars = Math.floor(w / (fontSize * 0.6));
      var name = e.name.length > maxChars ? e.name.slice(0, maxChars - 1) + '\u2026' : e.name;
      label.textContent = name;
      parent.appendChild(rect);
      parent.appendChild(label);
    } else {
      parent.appendChild(rect);
    }
  }

  function renderEvents(parent, topY, height) {
    var visible = data.events.filter(function (ev) {
      var x = yearToX(ev.year);
      if (x < -10 || x > W + 10) return false;
      return matchesSearch(ev.name);
    });

    for (var i = 0; i < visible.length; i++) {
      var ev = visible[i];
      var x = yearToX(ev.year);
      var opacity = searchTerm && !matchesSearch(ev.name) ? 0.1 : (0.3 + ev.confidence * 0.6);

      // Vertical line
      var line = svgEl('line', {
        x1: x, y1: topY, x2: x, y2: topY + height,
        stroke: '#58a6ff',
        'stroke-width': 0.5,
        'stroke-dasharray': '2,4',
        opacity: opacity * 0.3,
      });
      parent.appendChild(line);

      // Marker
      var markerY = topY + 16 + (i % 5) * 14;
      var marker = svgEl('text', {
        x: x, y: markerY,
        'text-anchor': 'middle',
        fill: '#58a6ff',
        'font-size': EVENT_MARKER_R * 2.2,
        opacity: opacity,
        'data-event-id': ev.id,
      });
      marker.textContent = EVENT_SHAPES[ev.type] || EVENT_SHAPES.OTHER;
      marker.style.cursor = 'pointer';

      (function (ev, marker, opacity) {
        marker.addEventListener('mouseenter', function (e) {
          marker.setAttribute('opacity', '1');
          marker.setAttribute('font-size', String(EVENT_MARKER_R * 3));
          showTooltip(e, eventTooltip(ev));
        });
        marker.addEventListener('mouseleave', function () {
          marker.setAttribute('opacity', String(opacity));
          marker.setAttribute('font-size', String(EVENT_MARKER_R * 2.2));
          hideTooltip();
        });
        marker.addEventListener('click', function () {
          window.open('/v1/events/' + ev.id, '_blank');
        });
      })(ev, marker, opacity);

      parent.appendChild(marker);
    }
  }

  function renderChains(parent, yStart) {
    var y = yStart;
    var visibleChains = data.chains.filter(function (ch) {
      if (!matchesSearch(ch.name)) {
        // Also check if any link entity matches
        var any = false;
        for (var j = 0; j < ch.links.length; j++) {
          if (matchesSearch(ch.links[j].entity_name || '')) { any = true; break; }
        }
        if (!any) return false;
      }
      return ch.links.length > 1;
    });

    for (var ci = 0; ci < visibleChains.length; ci++) {
      var ch = visibleChains[ci];
      var links = ch.links;
      var chainY = y;

      // Chain label
      var labelX = 8;
      var lbl = svgEl('text', {
        x: labelX, y: chainY + 4,
        fill: '#8b949e',
        'font-size': '10',
        'font-weight': '600',
        'font-family': "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      });
      lbl.textContent = ch.name;
      parent.appendChild(lbl);
      chainY += 12;

      // Draw each link as a bar with connecting lines
      var prevEndX = null;
      for (var li = 0; li < links.length; li++) {
        var lk = links[li];
        var startY_lk = lk.entity_year_start;
        var endY_lk = lk.entity_year_end || MAX_YEAR;
        var x1 = yearToX(startY_lk);
        var x2 = yearToX(endY_lk);
        if (x2 < 0 || x1 > W) { prevEndX = x2; continue; }

        x1 = Math.max(0, x1);
        x2 = Math.min(W, x2);
        var barW = Math.max(2, x2 - x1);

        // Connecting line from previous entity
        if (prevEndX !== null && li > 0) {
          var connX = yearToX(lk.year || startY_lk);
          var connColor = lk.violent ? '#f85149' : '#3fb950';
          parent.appendChild(svgEl('line', {
            x1: Math.min(W, Math.max(0, prevEndX)), y1: chainY + 3,
            x2: Math.min(W, Math.max(0, connX)), y2: chainY + 3,
            stroke: connColor,
            'stroke-width': 2,
            'stroke-dasharray': lk.violent ? '3,2' : 'none',
          }));

          // Transition marker
          var txX = clamp(connX, 0, W);
          var txCircle = svgEl('circle', {
            cx: txX, cy: chainY + 3, r: CHAIN_LINK_R,
            fill: connColor,
            stroke: '#161b22',
            'stroke-width': 1,
          });
          txCircle.style.cursor = 'pointer';
          (function(lk, txCircle) {
            txCircle.addEventListener('mouseenter', function(e) {
              showTooltip(e, chainTransitionTooltip(lk));
            });
            txCircle.addEventListener('mouseleave', hideTooltip);
          })(lk, txCircle);
          parent.appendChild(txCircle);
        }

        // Entity bar in chain
        var color = typeColor('other');
        parent.appendChild(svgEl('rect', {
          x: x1, y: chainY, width: barW, height: ENTITY_BAR_HEIGHT,
          rx: 2, ry: 2,
          fill: '#58a6ff',
          opacity: 0.5,
        }));

        // Entity name label
        if (barW > 30) {
          var cLabel = svgEl('text', {
            x: x1 + 3, y: chainY + ENTITY_BAR_HEIGHT - 1,
            fill: '#e6edf3',
            'font-size': '9',
            'font-family': "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
            'pointer-events': 'none',
          });
          var maxC = Math.floor(barW / 5.4);
          var n = (lk.entity_name || '?');
          cLabel.textContent = n.length > maxC ? n.slice(0, maxC - 1) + '\u2026' : n;
          parent.appendChild(cLabel);
        }

        prevEndX = x2;
      }

      y = chainY + ENTITY_BAR_HEIGHT + ENTITY_GAP + 8;
    }

    return y + 10;
  }

  // ── Tooltips ──────────────────────────────────────────────────

  function entityTooltip(e) {
    var end = e.year_end ? formatYear(e.year_end) : 'ongoing';
    return '<div class="tl-tooltip-title">' + escHtml(e.name) +
      '<span class="tl-tooltip-type" style="background:' + typeColor(e.type) + '22;color:' + typeColor(e.type) + '">' + escHtml(e.type) + '</span></div>' +
      '<div class="tl-tooltip-meta">' + formatYear(e.year_start) + ' \u2192 ' + end +
      ' &middot; confidence: ' + (e.confidence * 100).toFixed(0) + '%</div>';
  }

  function eventTooltip(ev) {
    var dateStr = formatYear(ev.year);
    if (ev.precision === 'DAY' && ev.month && ev.day) {
      dateStr = ev.day + '/' + ev.month + '/' + (ev.year < 0 ? Math.abs(ev.year) + ' BCE' : ev.year + ' CE');
    } else if (ev.precision === 'MONTH' && ev.month) {
      dateStr = ev.month + '/' + (ev.year < 0 ? Math.abs(ev.year) + ' BCE' : ev.year + ' CE');
    }
    return '<div class="tl-tooltip-title">' + escHtml(ev.name) + '</div>' +
      '<div class="tl-tooltip-meta">' + escHtml(ev.type) + ' &middot; ' + dateStr +
      ' &middot; confidence: ' + (ev.confidence * 100).toFixed(0) + '%</div>';
  }

  function chainTransitionTooltip(lk) {
    var parts = [];
    if (lk.transition) parts.push(escHtml(lk.transition));
    if (lk.year) parts.push(formatYear(lk.year));
    if (lk.violent) parts.push('<span style="color:#f85149">violent</span>');
    return '<div class="tl-tooltip-title">' + escHtml(lk.entity_name || '?') + '</div>' +
      '<div class="tl-tooltip-meta">' + (parts.join(' &middot; ') || 'transition') + '</div>';
  }

  function showTooltip(mouseEv, html) {
    tooltip.innerHTML = html;
    tooltip.classList.add('visible');
    positionTooltip(mouseEv.clientX, mouseEv.clientY);
  }

  function positionTooltip(mx, my) {
    var tw = tooltip.offsetWidth;
    var th = tooltip.offsetHeight;
    var x = mx + 12;
    var y = my + 12;
    if (x + tw > window.innerWidth - 8) x = mx - tw - 12;
    if (y + th > window.innerHeight - 8) y = my - th - 12;
    tooltip.style.left = x + 'px';
    tooltip.style.top = y + 'px';
  }

  function hideTooltip() {
    tooltip.classList.remove('visible');
  }

  // ── Zoom / Pan ────────────────────────────────────────────────

  function zoom(delta, centerX) {
    var centerYear = xToYear(centerX);
    var span = viewEnd - viewStart;
    var factor = delta > 0 ? 0.85 : 1.18;
    var newSpan = clamp(span * factor, 5, MAX_YEAR - MIN_YEAR + 200);

    var ratio = (centerYear - viewStart) / span;
    viewStart = centerYear - newSpan * ratio;
    viewEnd = viewStart + newSpan;

    // Clamp to bounds
    if (viewStart < MIN_YEAR) { viewStart = MIN_YEAR; viewEnd = viewStart + newSpan; }
    if (viewEnd > MAX_YEAR) { viewEnd = MAX_YEAR; viewStart = viewEnd - newSpan; }

    updateZoomSlider();
    render();
  }

  function setView(start, end) {
    viewStart = start;
    viewEnd = end;
    scrollY = 0;
    updateZoomSlider();
    render();
  }

  function updateZoomSlider() {
    var slider = document.getElementById('zoom-slider');
    if (!slider) return;
    var span = viewEnd - viewStart;
    var totalSpan = MAX_YEAR - MIN_YEAR;
    // logarithmic mapping
    var pct = 1 - (Math.log(span) - Math.log(5)) / (Math.log(totalSpan) - Math.log(5));
    slider.value = clamp(pct * 100, 0, 100);
  }

  // ── Event Handlers ────────────────────────────────────────────

  function onWheel(e) {
    e.preventDefault();
    if (e.ctrlKey || e.metaKey) {
      // Ctrl+Wheel = zoom
      var rect = mainEl.getBoundingClientRect();
      zoom(e.deltaY < 0 ? 1 : -1, e.clientX - rect.left);
    } else if (e.shiftKey) {
      // Shift+Wheel = horizontal pan
      var span = viewEnd - viewStart;
      var panPx = e.deltaY || e.deltaX;
      var panYears = (panPx / W) * span * 2;
      viewStart += panYears;
      viewEnd += panYears;
      render();
    } else {
      // Normal wheel = zoom (default behavior for timeline)
      var rect = mainEl.getBoundingClientRect();
      zoom(e.deltaY < 0 ? 1 : -1, e.clientX - rect.left);
    }
  }

  function onMouseDown(e) {
    if (e.button !== 0) return;
    isDragging = true;
    dragStartX = e.clientX;
    dragStartPan = viewStart;
    mainEl.classList.add('grabbing');
  }

  function onMouseMove(e) {
    if (!isDragging) return;
    var dx = e.clientX - dragStartX;
    var span = viewEnd - viewStart;
    var yearDelta = -(dx / W) * span;
    viewStart = dragStartPan + yearDelta;
    viewEnd = viewStart + span;
    render();
  }

  function onMouseUp() {
    isDragging = false;
    mainEl.classList.remove('grabbing');
  }

  // Touch events for mobile
  function onTouchStart(e) {
    if (e.touches.length === 1) {
      isDragging = true;
      dragStartX = e.touches[0].clientX;
      dragStartPan = viewStart;
    } else if (e.touches.length === 2) {
      isDragging = false;
      lastTouchDist = Math.hypot(
        e.touches[1].clientX - e.touches[0].clientX,
        e.touches[1].clientY - e.touches[0].clientY
      );
      lastTouchX = (e.touches[0].clientX + e.touches[1].clientX) / 2;
    }
  }

  function onTouchMove(e) {
    e.preventDefault();
    if (e.touches.length === 1 && isDragging) {
      var dx = e.touches[0].clientX - dragStartX;
      var span = viewEnd - viewStart;
      var yearDelta = -(dx / W) * span;
      viewStart = dragStartPan + yearDelta;
      viewEnd = viewStart + span;
      render();
    } else if (e.touches.length === 2) {
      var dist = Math.hypot(
        e.touches[1].clientX - e.touches[0].clientX,
        e.touches[1].clientY - e.touches[0].clientY
      );
      var cx = (e.touches[0].clientX + e.touches[1].clientX) / 2;
      var rect = mainEl.getBoundingClientRect();
      if (lastTouchDist > 0) {
        zoom(dist > lastTouchDist ? 1 : -1, cx - rect.left);
      }
      lastTouchDist = dist;
      lastTouchX = cx;
    }
  }

  function onTouchEnd() {
    isDragging = false;
    lastTouchDist = 0;
  }

  // ── Status bar ────────────────────────────────────────────────

  function updateStatus() {
    var span = viewEnd - viewStart;
    statusLeft.textContent = formatYear(Math.round(viewStart)) + ' \u2014 ' + formatYear(Math.round(viewEnd)) +
      ' (' + Math.round(span) + ' years)';
    statusRight.textContent = data.entities.length + ' entities \u00b7 ' +
      data.events.length + ' events \u00b7 ' + data.chains.length + ' chains';
  }

  // ── Resize ────────────────────────────────────────────────────

  function onResize() {
    var rect = mainEl.getBoundingClientRect();
    W = rect.width;
    H = rect.height;
    render();
  }

  // ── Init ──────────────────────────────────────────────────────

  async function init() {
    // DOM refs
    svg = document.getElementById('tl-svg');
    tooltip = document.getElementById('tl-tooltip');
    statusLeft = document.getElementById('tl-status-left');
    statusRight = document.getElementById('tl-status-right');
    loadingEl = document.getElementById('tl-loading');
    mainEl = document.getElementById('tl-main');

    // Compute initial size
    var rect = mainEl.getBoundingClientRect();
    W = rect.width;
    H = rect.height;

    // Load data
    try {
      await loadData();
    } catch (err) {
      loadingEl.querySelector('.tl-loading-text').textContent = 'Failed to load data: ' + err.message;
      return;
    }

    // Hide loading
    loadingEl.classList.add('hidden');

    // Initial render
    render();

    // ── Wire up controls ──

    // Era buttons
    document.querySelectorAll('[data-era]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        document.querySelectorAll('[data-era]').forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        var era = btn.getAttribute('data-era');
        switch (era) {
          case 'ancient': setView(-5000, -200); break;
          case 'medieval': setView(200, 1500); break;
          case 'modern': setView(1500, 2050); break;
          case 'all': default: setView(-5000, 2050); break;
        }
      });
    });

    // Layer toggles
    document.getElementById('layer-entities').addEventListener('change', function () {
      showEntities = this.checked; render();
    });
    document.getElementById('layer-events').addEventListener('change', function () {
      showEvents = this.checked; render();
    });
    document.getElementById('layer-chains').addEventListener('change', function () {
      showChains = this.checked; render();
    });

    // Search
    var searchInput = document.getElementById('tl-search-input');
    var searchTimeout;
    searchInput.addEventListener('input', function () {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(function () {
        searchTerm = searchInput.value.trim().toLowerCase();
        render();
      }, 200);
    });

    // Zoom slider
    document.getElementById('zoom-slider').addEventListener('input', function () {
      var pct = parseInt(this.value, 10) / 100;
      var totalSpan = MAX_YEAR - MIN_YEAR;
      var span = Math.exp(Math.log(5) + (1 - pct) * (Math.log(totalSpan) - Math.log(5)));
      var center = (viewStart + viewEnd) / 2;
      viewStart = center - span / 2;
      viewEnd = center + span / 2;
      if (viewStart < MIN_YEAR) { viewStart = MIN_YEAR; viewEnd = viewStart + span; }
      if (viewEnd > MAX_YEAR) { viewEnd = MAX_YEAR; viewStart = viewEnd - span; }
      render();
    });

    // Mouse events
    mainEl.addEventListener('wheel', onWheel, { passive: false });
    mainEl.addEventListener('mousedown', onMouseDown);
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);

    // Touch events
    mainEl.addEventListener('touchstart', onTouchStart, { passive: true });
    mainEl.addEventListener('touchmove', onTouchMove, { passive: false });
    mainEl.addEventListener('touchend', onTouchEnd, { passive: true });

    // Resize
    window.addEventListener('resize', onResize);

    // Mousemove for tooltip positioning
    mainEl.addEventListener('mousemove', function (e) {
      if (tooltip.classList.contains('visible')) {
        positionTooltip(e.clientX, e.clientY);
      }
    });
  }

  // Start
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
