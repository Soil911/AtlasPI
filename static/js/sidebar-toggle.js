// ═══════════════════════════════════════════════════════════════════
// AtlasPI — sidebar collapse toggle module (v6.51)
//
// Binds #sidebar-toggle to toggle .sidebar-collapsed on #app.
// Persists in localStorage. On mobile (<768px), uses a different
// class (sidebar-mobile-open) since the sidebar is overlay, not inline.
// ═══════════════════════════════════════════════════════════════════

(function() {
  'use strict';

  const KEY = 'atlaspi-sidebar-collapsed';

  function isMobile() {
    return window.matchMedia('(max-width: 768px)').matches;
  }

  function apply(collapsed) {
    const app = document.getElementById('app');
    if (!app) return;
    if (isMobile()) {
      // Mobile: opposite semantic — sidebar overlay, show/hide
      if (collapsed) {
        app.classList.remove('sidebar-mobile-open');
      } else {
        app.classList.add('sidebar-mobile-open');
      }
    } else {
      if (collapsed) {
        app.classList.add('sidebar-collapsed');
      } else {
        app.classList.remove('sidebar-collapsed');
      }
    }
    const btn = document.getElementById('sidebar-toggle');
    if (btn) btn.setAttribute('aria-pressed', String(!collapsed));

    // Invalidate Leaflet map size after layout shift
    setTimeout(() => {
      if (typeof map !== 'undefined' && map && typeof map.invalidateSize === 'function') {
        map.invalidateSize();
      }
    }, 280); // slightly after CSS transition (250ms)
  }

  function init() {
    const btn = document.getElementById('sidebar-toggle');
    if (!btn) return;

    // Restore state: default = expanded on desktop, collapsed on mobile
    let stored = null;
    try { stored = localStorage.getItem(KEY); } catch (_) {}
    let collapsed;
    if (stored === null) {
      collapsed = isMobile();  // mobile: start collapsed, desktop: start open
    } else {
      collapsed = stored === '1';
    }
    apply(collapsed);

    btn.addEventListener('click', () => {
      const app = document.getElementById('app');
      if (!app) return;
      const currentlyCollapsed = isMobile()
        ? !app.classList.contains('sidebar-mobile-open')
        : app.classList.contains('sidebar-collapsed');
      const next = !currentlyCollapsed;
      apply(next);
      try { localStorage.setItem(KEY, next ? '1' : '0'); } catch (_) {}
    });

    // Re-apply on resize (mobile ↔ desktop breakpoint)
    let resizeTimer;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => {
        let s = null;
        try { s = localStorage.getItem(KEY); } catch (_) {}
        apply(s === null ? isMobile() : s === '1');
      }, 150);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
