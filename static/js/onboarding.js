// ═══════════════════════════════════════════════════════════════════
// AtlasPI — onboarding overlay module (v6.50)
//
// First-time visitor gets a 3-step intro overlay. Dismissed via button
// or Skip. Persists in localStorage so it doesn't show again.
// ═══════════════════════════════════════════════════════════════════

(function() {
  'use strict';

  const KEY = 'atlaspi-onboarding-seen-v1';

  function show() {
    const overlay = document.getElementById('onboarding');
    if (overlay) overlay.style.display = 'flex';
  }

  function hide() {
    const overlay = document.getElementById('onboarding');
    if (overlay) overlay.style.display = 'none';
    try { localStorage.setItem(KEY, '1'); } catch (_) {}
  }

  window.showOnboarding = show;   // manual trigger (future: help menu)
  window.hideOnboarding = hide;

  function init() {
    const skipBtn = document.getElementById('onboarding-skip');
    const doneBtn = document.getElementById('onboarding-done');
    const overlay = document.getElementById('onboarding');
    if (!overlay) return;

    if (skipBtn) skipBtn.addEventListener('click', hide);
    if (doneBtn) doneBtn.addEventListener('click', hide);

    // Close on backdrop click (but not card click)
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) hide();
    });

    // Close on Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && overlay.style.display === 'flex') hide();
    });

    // Show on first visit (localStorage miss)
    let seen = null;
    try { seen = localStorage.getItem(KEY); } catch (_) {}
    if (!seen) {
      // Slight delay so the underlying page renders first
      setTimeout(show, 600);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
