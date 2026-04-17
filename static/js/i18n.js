// ═══════════════════════════════════════════════════════════════════
// AtlasPI — i18n module (v6.46)
//
// Extracted from app.js monolite. Provides:
//   - window.I18N: translations dictionary (it + en)
//   - window.t(key): lookup function
//   - window.lang: current language
//   - window.initLang() / switchLang() / applyLangUI()
//
// NO module system (loaded via <script>). All exports via window.*.
// ═══════════════════════════════════════════════════════════════════

(function() {
  'use strict';

  window.lang = localStorage.getItem('atlaspi-lang') || 'it';

  window.I18N = {
    it: {
      search: 'Cerca per nome, anche varianti...',
      year: 'Anno', status: 'Status',
      confirmed: 'Confermato', uncertain: 'Incerto', disputed: 'Contestato',
      type: 'Tipo', sort_label: 'Ordina', sort_default: 'Predefinito',
      sort_name: 'Nome A-Z', sort_year: 'Anno', sort_conf: 'Affidabilit\u00e0',
      reset: 'Reset filtri', all: 'Tutti', loading: 'Caricamento...',
      no_results: 'Nessuna entit\u00e0 trovata', entities: 'entit\u00e0',
      sources: 'fonti', changes: 'cambi', contested: 'contestati',
      avg_conf: 'conf. media', info: 'Informazioni', reliability: 'Affidabilit\u00e0',
      names_section: 'Nomi e varianti (ETHICS-001)',
      territory_section: 'Cambiamenti territoriali (ETHICS-002)',
      sources_section: 'Fonti', ethics_section: 'Governance etica',
      period: 'Periodo', capital: 'Capitale', score: 'Score',
      today: 'oggi', present: 'presente', bc: 'a.C.',
      real_boundary: 'Confini da dataset accademici. Verificare le fonti per dettagli.',
      approx_boundary: 'Confini approssimativi a scopo dimostrativo.',
      pop_affected: 'Popolazione colpita',
      banner: 'Confini da fonti accademiche. Dati storici da Natural Earth e aourednik/historical-basemaps.',
      map_hint: "Seleziona un'entit\u00e0 dalla lista o clicca sulla mappa. Tasto destro per trovare entit\u00e0 vicine.",
      share: 'Condividi', link_copied: 'Link copiato negli appunti!',
      partial_data: 'dati parziali o incerti',
      contemporaries: 'Contemporanei',
      no_contemporaries: 'Nessun contemporaneo trovato',
      error_connection: 'Impossibile caricare i dati. Verifica che il server sia attivo.',
      error_detail: 'Errore nel caricamento dei dettagli.',
      keyboard_help: 'Scorciatoie tastiera',
      compare: 'Confronta',
      compare_select: "Ora clicca su un'altra entit\u00e0 per confrontarle",
      duration: 'Durata',
      temporal_overlap: 'Sovrapposizione temporale',
      years: 'anni',
      no_overlap: 'Nessuna sovrapposizione',
      view: 'Vedi',
      enter_to_search: 'Invio per cercare',
      navigate: 'naviga',
      nearby: 'Vicini',
      distance: 'Distanza',
      snapshot: 'Snapshot',
      active_in: 'Attive nel',
      events: 'eventi',
      events_overlay: 'Mostra eventi storici',
      events_hint: "Battaglie, trattati, fondazioni e altri eventi nell'anno selezionato.",
      event_actor: 'Attore',
      event_detail: 'Vedi dettaglio completo',
      event_year: 'Anno',
      event_date: 'Data',
      event_location: 'Luogo',
      event_main_actor: 'Attore principale',
      event_description: 'Descrizione',
      event_casualties: 'Vittime stimate',
      event_linked_entities: 'Entit\u00e0 collegate',
      event_error: "Errore nel caricamento dell'evento",
    },
    en: {
      search: 'Search by name, including variants...',
      year: 'Year', status: 'Status',
      confirmed: 'Confirmed', uncertain: 'Uncertain', disputed: 'Disputed',
      type: 'Type', sort_label: 'Sort', sort_default: 'Default',
      sort_name: 'Name A-Z', sort_year: 'Year', sort_conf: 'Reliability',
      reset: 'Reset filters', all: 'All', loading: 'Loading...',
      no_results: 'No entities found', entities: 'entities',
      sources: 'sources', changes: 'changes', contested: 'contested',
      avg_conf: 'avg conf.', info: 'Information', reliability: 'Reliability',
      names_section: 'Names & variants (ETHICS-001)',
      territory_section: 'Territory changes (ETHICS-002)',
      sources_section: 'Sources', ethics_section: 'Ethical governance',
      period: 'Period', capital: 'Capital', score: 'Score',
      today: 'today', present: 'present', bc: 'BC',
      real_boundary: 'Boundaries from academic datasets. Check sources for details.',
      approx_boundary: 'Approximate boundaries for demonstration.',
      pop_affected: 'Population affected',
      banner: 'Boundaries from academic sources. Data from Natural Earth and aourednik/historical-basemaps.',
      map_hint: 'Select an entity from the list or click the map. Right-click to find nearby entities.',
      share: 'Share', link_copied: 'Link copied to clipboard!',
      partial_data: 'partial or uncertain data',
      contemporaries: 'Contemporaries',
      no_contemporaries: 'No contemporaries found',
      error_connection: 'Unable to load data. Check if the server is running.',
      error_detail: 'Error loading details.',
      keyboard_help: 'Keyboard shortcuts',
      compare: 'Compare',
      compare_select: 'Now click another entity to compare them',
      duration: 'Duration',
      temporal_overlap: 'Temporal overlap',
      years: 'years',
      no_overlap: 'No overlap',
      view: 'View',
      enter_to_search: 'Enter to search',
      navigate: 'navigate',
      nearby: 'Nearby',
      distance: 'Distance',
      snapshot: 'Snapshot',
      active_in: 'Active in',
      events: 'events',
      events_overlay: 'Show historical events',
      events_hint: 'Battles, treaties, foundations and other events in the selected year.',
      event_actor: 'Actor',
      event_detail: 'View full detail',
      event_year: 'Year',
      event_date: 'Date',
      event_location: 'Location',
      event_main_actor: 'Main actor',
      event_description: 'Description',
      event_casualties: 'Estimated casualties',
      event_linked_entities: 'Linked entities',
      event_error: 'Error loading event',
    },
  };

  window.t = function t(key) {
    return (window.I18N[window.lang] || window.I18N.it)[key] || key;
  };

  window.initLang = function initLang() {
    const toggle = document.getElementById('lang-toggle');
    if (toggle) toggle.textContent = window.lang === 'it' ? 'EN' : 'IT';
    window.applyLangUI();
  };

  window.switchLang = function switchLang() {
    window.lang = window.lang === 'it' ? 'en' : 'it';
    localStorage.setItem('atlaspi-lang', window.lang);
    const toggle = document.getElementById('lang-toggle');
    if (toggle) toggle.textContent = window.lang === 'it' ? 'EN' : 'IT';
    window.applyLangUI();
    if (typeof pushUrlState === 'function') pushUrlState();
  };

  window.applyLangUI = function applyLangUI() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) searchInput.placeholder = window.t('search');
    const resetBtn = document.getElementById('reset-btn');
    if (resetBtn) resetBtn.textContent = window.t('reset');
    const banner = document.querySelector('.data-banner');
    if (banner) {
      banner.innerHTML = `<strong>${window.t('banner').split('.')[0]}.</strong> ${window.t('banner').split('.').slice(1).join('.')}`;
    }
    const info = document.getElementById('map-info');
    if (info) info.textContent = window.t('map_hint');
    // Note: chainsData, applyFilters, loadStats, renderChainsList are
    // declared in app.js. `function` declarations are on window; `let/const`
    // are NOT (script global scope). We use typeof guards.
    if (typeof applyFilters === 'function') applyFilters();
    if (typeof loadStats === 'function') loadStats();
    // v6.7 — re-render chain list with updated labels (chainsData is let, lookup global)
    if (typeof chainsData !== 'undefined' && chainsData && typeof renderChainsList === 'function') {
      renderChainsList();
    }
  };
})();
