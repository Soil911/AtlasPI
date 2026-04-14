/* AtlasPI landing — minimal vanilla JS, no dependencies */
(function () {
  'use strict';

  // ─── Footer year ────────────────────────────────────────────
  var yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

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
