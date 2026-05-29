/* AtlasPI — boundary lazy-load merge logic (Wave 1.3), extracted in Wave 2.6
 * for unit testing (audit #8: il frontend non aveva copertura automatica).
 *
 * Funzione PURA, senza dipendenze DOM/network: fonde il batch "full" di
 * /v1/entities (che porta boundary_geojson) nella lista canonica caricata da
 * /v1/entities/light. Regola critica: aggiorna SOLO boundary_geojson + campi
 * opzionali assenti; NON sovrascrive name/status/year/confidence (canonici dal
 * /light). app.js usa questa funzione se presente, con fallback inline identico
 * così un modulo mancante/bloccato non rompe mai il rendering della mappa.
 *
 * UMD: gira sia come <script> nel browser (window.AtlasBoundaryCache) sia in
 * Node (module.exports) per `node --test`.
 */
(function (root) {
  'use strict';

  /**
   * @param {Array<object>} allEntities  lista canonica (da /light), mutata in place
   * @param {Array<object>} batch        entità "full" da /v1/entities?year=
   * @returns {number} numero di entità effettivamente fuse
   */
  function mergeBoundaryBatch(allEntities, batch) {
    if (!Array.isArray(allEntities) || !Array.isArray(batch)) return 0;
    const byId = new Map();
    for (const e of allEntities) byId.set(e.id, e);
    let merged = 0;
    for (const full of batch) {
      const e = byId.get(full.id);
      if (!e) continue; // entità non in /light → ignora (light è la lista canonica)
      e.boundary_geojson = full.boundary_geojson;
      e._boundary_load_state = 'loaded';
      // Campi opzionali: riempi SOLO se assenti (no overwrite del canonico).
      if (!e.sources) e.sources = full.sources;
      if (!e.ethical_notes) e.ethical_notes = full.ethical_notes;
      if (!e.territory_changes) e.territory_changes = full.territory_changes;
      if (!e.name_variants) e.name_variants = full.name_variants;
      merged++;
    }
    return merged;
  }

  const api = { mergeBoundaryBatch };
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api; // Node (node --test)
  }
  root.AtlasBoundaryCache = api; // browser
})(typeof globalThis !== 'undefined' ? globalThis : this);
