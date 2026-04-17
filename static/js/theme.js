// ═══════════════════════════════════════════════════════════════════
// AtlasPI — theme module (v6.46)
//
// Dark/light theme toggle persistence.
//   - window.initTheme() — restore saved preference
//   - window.toggleTheme() — switch (bound to theme toggle button)
//   - window.applyTheme(theme) — apply to document
// ═══════════════════════════════════════════════════════════════════

(function() {
  'use strict';

  window.initTheme = function initTheme() {
    const saved = localStorage.getItem('atlaspi-theme') || 'dark';
    window.applyTheme(saved);
  };

  window.toggleTheme = function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    const next = current === 'dark' ? 'light' : 'dark';
    window.applyTheme(next);
    localStorage.setItem('atlaspi-theme', next);
  };

  window.applyTheme = function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    const btn = document.getElementById('theme-toggle');
    if (btn) btn.textContent = theme === 'dark' ? '☀️' : '🌙';
    // Invalidate map size after theme change (leaflet needs it after CSS vars swap).
    // `map` is declared as `let` in app.js, not on window. Lookup via typeof.
    setTimeout(() => {
      if (typeof map !== 'undefined' && map && typeof map.invalidateSize === 'function') {
        map.invalidateSize();
      }
    }, 100);
  };
})();
