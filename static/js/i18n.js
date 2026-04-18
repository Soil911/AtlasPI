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
      year: 'Anno:', status: 'Status:',
      region_legend: 'Regione:',
      confirmed: 'Confermato', uncertain: 'Incerto', disputed: 'Contestato',
      type: 'Tipo:', sort_label: 'Ordina:', sort_default: 'Predefinito',
      sort_name: 'Nome A-Z', sort_year: 'Anno (antico-recente)', sort_conf: 'Affidabilit\u00e0 (alta-bassa)',
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
      // v6.50: era chips + onboarding + Ask Claude
      era_bronze: '🏺 Età del Bronzo',
      era_classical: '🏛️ Antichità',
      era_roman_peak: '🦅 Roma imperiale',
      era_medieval: '⚔️ Medioevo',
      era_mongol: '🏯 Mondo Mongolo',
      era_discovery: '⛵ Età delle Scoperte',
      era_revolutions: '🗽 Rivoluzioni',
      era_world_wars: '⚙️ Grande Guerra',
      era_today: '📡 Oggi',
      ask_claude: 'Ask Claude',
      onb_title: 'Benvenuto in AtlasPI 👋',
      // v6.66: i numeri reali vengono iniettati a runtime via injectLiveStats()
      onb_sub: 'Il database geografico storico per esplorare {entities} imperi, {events} eventi, {rulers} sovrani, {sites} siti archeologici.',
      onb_step1_title: "Sposta lo slider dell'anno",
      onb_step1_desc: 'O clicca le chip (es. "🦅 Roma imperiale") per saltare a epoche specifiche.',
      onb_step2_title: "Clicca un'entità sulla mappa",
      onb_step2_desc: 'Apre il pannello con confini, capitale, fonti accademiche, ETHICS notes.',
      onb_step3_title: '"Ask Claude" in alto destra',
      onb_step3_desc: 'Copia un prompt precompilato per spiegarti quello che stai vedendo con AI.',
      onb_skip: 'Skip',
      onb_start: 'Inizia!',
      claude_prompt_copied: 'Prompt copiato negli appunti! Incollalo in Claude.',
      // v6.62: header / navigation / controls
      theme_toggle_title: 'Cambia tema',
      theme_toggle_aria: 'Cambia tema chiaro/scuro',
      lang_toggle_title: 'Switch language',
      lang_toggle_aria: 'Cambia lingua',
      nav_search_title: 'Ricerca avanzata nel dataset',
      nav_timeline_title: 'Timeline interattiva',
      nav_compare_title: 'Confronta entità storiche',
      nav_embed_title: 'Versione embed per iframe',
      nav_apidocs_title: 'Documentazione API interattiva',
      nav_openapi_title: 'Documentazione API OpenAPI',
      sidebar_toggle_title: 'Mostra/nascondi pannello filtri',
      sidebar_toggle_aria: 'Toggle sidebar',
      ask_claude_title: 'Chiedi a Claude usando i dati di AtlasPI',
      ask_claude_aria: 'Apri Claude con prompt precompilato',
      // search
      search_aria: 'Cerca entità per nome',
      search_btn_title: 'Cerca',
      search_btn_aria: 'Avvia ricerca',
      autocomplete_aria: 'Suggerimenti ricerca',
      // year control
      year_input_aria: 'Inserisci anno esatto',
      year_go_aria: 'Applica anno',
      year_slider_aria: 'Seleziona anno storico',
      play_btn_title: 'Riproduci timeline',
      play_btn_aria: 'Avvia playback storico',
      play_speed_aria: 'Velocità playback',
      era_chips_aria: "Salta a un'epoca storica",
      continent_chips_aria: 'Filtra per continente',
      type_chips_aria: "Filtra per tipo di entità",
      sort_aria: 'Ordina risultati',
      // detail panel
      close_detail_aria: 'Chiudi pannello dettagli',
      // map
      events_overlay_title: 'Mostra eventi storici',
      map_scroll_hint: 'Clicca sulla mappa per abilitare lo zoom con la rotella',
      map_fullscreen_title: 'Schermo intero',
      map_fullscreen_aria: 'Mappa a schermo intero',
      map_fit_title: 'Mostra tutte le entità',
      map_fit_aria: 'Zoom su tutte le entità',
      reset_filters_aria: 'Azzera tutti i filtri',
      // v6.66: footer legend + scorciatoie + welcome modal
      legend_aria: 'Legenda colori mappa',
      legend_real: 'Reale',
      legend_approx: 'Approssimato',
      footer_note_tail: '&mdash; Dati storici con governance etica &middot; <kbd style="font-size:0.9em;padding:1px 4px;background:#1c2333;border:1px solid #30363d;border-radius:3px;color:#58a6ff">?</kbd> scorciatoie &middot; 34 tools MCP',
    },
    en: {
      search: 'Search by name, including variants...',
      year: 'Year:', status: 'Status:',
      region_legend: 'Region:',
      confirmed: 'Confirmed', uncertain: 'Uncertain', disputed: 'Disputed',
      type: 'Type:', sort_label: 'Sort:', sort_default: 'Default',
      sort_name: 'Name A-Z', sort_year: 'Year (old-recent)', sort_conf: 'Reliability (high-low)',
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
      // v6.50: era chips + onboarding + Ask Claude
      era_bronze: '🏺 Bronze Age',
      era_classical: '🏛️ Antiquity',
      era_roman_peak: '🦅 Roman Peak',
      era_medieval: '⚔️ Middle Ages',
      era_mongol: '🏯 Mongol World',
      era_discovery: '⛵ Age of Discovery',
      era_revolutions: '🗽 Revolutions',
      era_world_wars: '⚙️ Great War',
      era_today: '📡 Today',
      ask_claude: 'Ask Claude',
      onb_title: 'Welcome to AtlasPI 👋',
      // v6.66: numbers injected at runtime via injectLiveStats()
      onb_sub: 'The historical geography database — explore {entities} empires, {events} events, {rulers} rulers, {sites} archaeological sites.',
      onb_step1_title: 'Move the year slider',
      onb_step1_desc: 'Or click a chip (e.g. "🦅 Roman Peak") to jump to a specific era.',
      onb_step2_title: 'Click an entity on the map',
      onb_step2_desc: 'Opens the panel with boundaries, capital, academic sources, ETHICS notes.',
      onb_step3_title: '"Ask Claude" top right',
      onb_step3_desc: 'Copies a pre-filled prompt to explain what you see using AI.',
      onb_skip: 'Skip',
      onb_start: "Let's go!",
      claude_prompt_copied: 'Prompt copied to clipboard! Paste it into Claude.',
      // v6.62: header / navigation / controls (EN)
      theme_toggle_title: 'Switch theme',
      theme_toggle_aria: 'Toggle light/dark theme',
      lang_toggle_title: 'Switch language',
      lang_toggle_aria: 'Switch language',
      nav_search_title: 'Advanced dataset search',
      nav_timeline_title: 'Interactive timeline',
      nav_compare_title: 'Compare historical entities',
      nav_embed_title: 'Embed version for iframe',
      nav_apidocs_title: 'Interactive API documentation',
      nav_openapi_title: 'OpenAPI documentation',
      sidebar_toggle_title: 'Show/hide filters panel',
      sidebar_toggle_aria: 'Toggle sidebar',
      ask_claude_title: 'Ask Claude using AtlasPI data',
      ask_claude_aria: 'Open Claude with preset prompt',
      // search
      search_aria: 'Search entities by name',
      search_btn_title: 'Search',
      search_btn_aria: 'Start search',
      autocomplete_aria: 'Search suggestions',
      // year control
      year_input_aria: 'Enter exact year',
      year_go_aria: 'Apply year',
      year_slider_aria: 'Select historical year',
      play_btn_title: 'Play timeline',
      play_btn_aria: 'Start historical playback',
      play_speed_aria: 'Playback speed',
      era_chips_aria: 'Jump to a historical era',
      continent_chips_aria: 'Filter by continent',
      type_chips_aria: 'Filter by entity type',
      sort_aria: 'Sort results',
      // detail panel
      close_detail_aria: 'Close detail panel',
      // map
      events_overlay_title: 'Show historical events',
      map_scroll_hint: 'Click the map to enable zoom with the scroll wheel',
      map_fullscreen_title: 'Fullscreen',
      map_fullscreen_aria: 'Map fullscreen',
      map_fit_title: 'Show all entities',
      map_fit_aria: 'Zoom to all entities',
      reset_filters_aria: 'Reset all filters',
      // v6.66: footer legend + shortcuts + welcome modal (EN)
      legend_aria: 'Map color legend',
      legend_real: 'Real',
      legend_approx: 'Approximate',
      footer_note_tail: '&mdash; Historical data with ethical governance &middot; <kbd style="font-size:0.9em;padding:1px 4px;background:#1c2333;border:1px solid #30363d;border-radius:3px;color:#58a6ff">?</kbd> shortcuts &middot; 34 MCP tools',
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

  // v6.66: simple {key} placeholder interpolator. Sostituisce
  // {entities}, {events}, {rulers}, {sites} con numeri live (o fallback).
  // Assicura che il testo tradotto resti veritiero in qualunque lingua.
  function interpolate(str, vars) {
    if (!str || !vars) return str;
    return str.replace(/\{(\w+)\}/g, function (_, k) {
      return vars[k] != null ? vars[k] : '{' + k + '}';
    });
  }
  window.i18nVars = window.i18nVars || {};

  // v6.66: esponi una funzione per aggiornare i numeri live e ri-renderare.
  window.setI18nStats = function (stats) {
    window.i18nVars = Object.assign({}, window.i18nVars, stats || {});
    if (typeof window.applyLangUI === 'function') window.applyLangUI();
  };

  window.applyLangUI = function applyLangUI() {
    // v6.66: aggiorna html[lang] così screen reader e Chrome translator
    // vedono la lingua corrente. ETHICS: accessibilità reale, non solo UI.
    document.documentElement.lang = window.lang;

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

    const vars = window.i18nVars || {};

    // v6.48.2: generic [data-i18n] translator — any element with
    // data-i18n="key" gets its textContent replaced with t(key).
    // v6.66: se il testo contiene {placeholder}, interpola con i18nVars.
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      const translated = window.t(key);
      // Only replace if translation exists and differs from key (fallback)
      if (translated && translated !== key) {
        el.textContent = interpolate(translated, vars);
      }
    });

    // v6.66: data-i18n-html per stringhe con markup (es. footer).
    document.querySelectorAll('[data-i18n-html]').forEach(el => {
      const key = el.getAttribute('data-i18n-html');
      const translated = window.t(key);
      if (translated && translated !== key) {
        el.innerHTML = interpolate(translated, vars);
      }
    });

    // v6.62: also handle title, aria-label, placeholder attributes
    // via dedicated data-i18n-* keys. Closes the "EN translation leak ~40%"
    // issue from audit #03.
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
      const key = el.getAttribute('data-i18n-title');
      const translated = window.t(key);
      if (translated && translated !== key) el.title = translated;
    });
    document.querySelectorAll('[data-i18n-aria-label]').forEach(el => {
      const key = el.getAttribute('data-i18n-aria-label');
      const translated = window.t(key);
      if (translated && translated !== key) el.setAttribute('aria-label', translated);
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      const translated = window.t(key);
      if (translated && translated !== key) el.placeholder = translated;
    });
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
