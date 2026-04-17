// ═══════════════════════════════════════════════════════════════════
// AtlasPI — utility functions module (v6.46)
//
// Pure helpers, no DOM side effects (except esc which uses DOM for escape).
//   - window.fmtY(year): format year ("a.C." / "BC" via i18n)
//   - window.esc(str): HTML-escape string
//   - window.isReal(entity): check if boundary has enough points to be "real"
// ═══════════════════════════════════════════════════════════════════

(function() {
  'use strict';

  window.fmtY = function fmtY(y) {
    if (y < 0) return `${Math.abs(y)} ${window.t('bc')}`;
    return String(y);
  };

  window.esc = function esc(s) {
    if (!s) return '';
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  };

  window.isReal = function isReal(e) {
    if (!e.boundary_geojson) return false;
    const g = e.boundary_geojson;
    let pts = 0;
    if (g.type === 'Polygon') pts = g.coordinates.reduce((s, r) => s + r.length, 0);
    else if (g.type === 'MultiPolygon') pts = g.coordinates.reduce((s, p) => s + p.reduce((s2, r) => s2 + r.length, 0), 0);
    return pts > 50;
  };
})();
