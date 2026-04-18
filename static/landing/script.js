/* AtlasPI landing — minimal vanilla JS, no dependencies */
(function () {
  'use strict';

  // ─── Footer year ────────────────────────────────────────────
  var yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  // ─── v6.66: Live stats injection ────────────────────────────
  // Single source of truth: popola tutti gli [data-live="<key>"] da /health
  // + endpoint /v1/... per i conteggi, evitando drift statico.
  function fmt(n) {
    // Formatta migliaia con virgola (1034 -> "1,034")
    return typeof n === 'number' ? n.toLocaleString('en-US') : String(n);
  }
  function setLive(key, value) {
    var nodes = document.querySelectorAll('[data-live="' + key + '"]');
    for (var i = 0; i < nodes.length; i++) nodes[i].textContent = value;
  }
  function fetchCount(url) {
    return fetch(url, { cache: 'no-store' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (j) {
        if (!j) return null;
        if (typeof j.count === 'number') return j.count;
        if (typeof j.total === 'number') return j.total;
        if (typeof j.entity_count === 'number') return j.entity_count;
        return null;
      })
      .catch(function () { return null; });
  }
  // Fire-and-forget: evita flash; i fallback statici restano sensati.
  (function hydrateLiveStats() {
    if (!('fetch' in window)) return;
    fetch('/health', { cache: 'no-store' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (h) {
        if (h && h.version) setLive('version', h.version);
        if (h && typeof h.entity_count === 'number') setLive('entity_count', fmt(h.entity_count));
      })
      .catch(function () { /* noop */ });
    // Conteggi paralleli: ognuno indipendente, failure silente.
    var calls = [
      ['event_count',  '/v1/events?limit=1'],
      ['period_count', '/v1/periods?limit=1'],
      ['city_count',   '/v1/cities?limit=1'],
      ['route_count',  '/v1/routes?limit=1'],
      ['chain_count',  '/v1/chains?limit=1'],
      ['ruler_count',  '/v1/rulers?limit=1'],
      ['site_count',   '/v1/sites?limit=1'],
      ['language_count', '/v1/languages?limit=1'],
    ];
    calls.forEach(function (pair) {
      fetchCount(pair[1]).then(function (n) {
        if (n !== null) setLive(pair[0], fmt(n));
      });
    });
  })();

  // ─── Smooth scroll for anchor links (browser handles via CSS,
  //     but we add focus management for a11y) ─────────────────
  document.querySelectorAll('a[href^="#"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var id = a.getAttribute('href');
      if (!id || id === '#' || id.length < 2) return;
      var target = document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      // Move focus for keyboard / SR users
      target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
      // Update URL without jumping
      if (history.pushState) history.pushState(null, '', id);
    });
  });

  // ─── Tab switcher (curl / Python / JS) ──────────────────────
  var tabs = document.querySelectorAll('.tab');
  var panels = document.querySelectorAll('.tab-panel');

  function activateTab(name) {
    tabs.forEach(function (t) {
      var isActive = t.dataset.tab === name;
      t.classList.toggle('active', isActive);
      t.setAttribute('aria-selected', isActive ? 'true' : 'false');
    });
    panels.forEach(function (p) {
      var isActive = p.id === 'tab-' + name;
      p.classList.toggle('active', isActive);
      if (isActive) {
        p.removeAttribute('hidden');
      } else {
        p.setAttribute('hidden', '');
      }
    });
  }

  tabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      activateTab(tab.dataset.tab);
    });
    // Arrow-key navigation between tabs (a11y)
    tab.addEventListener('keydown', function (e) {
      var arr = Array.prototype.slice.call(tabs);
      var idx = arr.indexOf(tab);
      if (e.key === 'ArrowRight') {
        e.preventDefault();
        var next = arr[(idx + 1) % arr.length];
        next.focus(); activateTab(next.dataset.tab);
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        var prev = arr[(idx - 1 + arr.length) % arr.length];
        prev.focus(); activateTab(prev.dataset.tab);
      }
    });
  });

  // ─── Copy-to-clipboard for code blocks ──────────────────────
  function fallbackCopy(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.position = 'absolute';
    ta.style.left = '-9999px';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); } catch (e) { /* noop */ }
    document.body.removeChild(ta);
  }

  document.querySelectorAll('.copy-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var targetId = btn.dataset.copyTarget;
      var node = document.getElementById(targetId);
      if (!node) return;
      var text = node.textContent || '';

      var done = function () {
        var original = btn.textContent;
        btn.textContent = 'Copied!';
        btn.classList.add('copied');
        setTimeout(function () {
          btn.textContent = original;
          btn.classList.remove('copied');
        }, 1500);
      };

      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, function () {
          fallbackCopy(text); done();
        });
      } else {
        fallbackCopy(text); done();
      }
    });
  });

  // ─── Animate hero year counter (cosmetic, low-cost) ─────────
  var meta = document.querySelector('.meta-year');
  if (meta && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var years = [-3000, -500, 100, 476, 800, 1066, 1453, 1500, 1776, 1914, 2024];
    var i = 0;
    setInterval(function () {
      i = (i + 1) % years.length;
      var y = years[i];
      meta.textContent = y < 0 ? Math.abs(y) + ' BCE' : String(y);
    }, 2200);
  }
})();
