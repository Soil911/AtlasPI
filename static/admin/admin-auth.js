/* AtlasPI admin auth (traffic-fix #2) — token affidabile per le dashboard admin.
 *
 * Le shell admin dipendevano dal caching Basic-Auth del browser (fragile → 401
 * intermittenti). Qui: il token è chiesto UNA volta, salvato in localStorage e
 * inviato come header X-Admin-Token su TUTTE le chiamate /admin/*.
 *
 * Robustezza:
 *  - il wrapper di fetch è installato SUBITO (prima di qualsiasi prompt);
 *  - il prompt è in try/catch (un prompt negato non rompe il wrapper);
 *  - su 401 si ripulisce il token e si richiede UNA sola volta (flag `declined`),
 *    SENZA location.reload() → niente loop/tempesta di richieste.
 *
 * Le shell HTML sono pubbliche (nessun dato dentro); i dati restano protetti da
 * verify_admin lato server. Includere PRIMA degli altri <script>.
 */
(function () {
  'use strict';
  var KEY = 'atlaspi_admin_token';
  var prompting = false;   // evita prompt concorrenti (chiamate parallele)
  var declined = false;    // dopo un prompt annullato, non insistere fino al reload

  function getToken() { try { return localStorage.getItem(KEY) || ''; } catch (e) { return ''; } }
  function setToken(t) { try { localStorage.setItem(KEY, t); } catch (e) { /* noop */ } }
  function clearToken() { try { localStorage.removeItem(KEY); } catch (e) { /* noop */ } }

  function askToken() {
    var existing = getToken();
    if (existing) return existing;
    if (prompting || declined) return '';
    prompting = true;
    var t = '';
    try { t = (window.prompt("AtlasPI — inserisci l'admin token:") || '').trim(); } catch (e) { t = ''; }
    prompting = false;
    if (t) { setToken(t); } else { declined = true; }
    return t;
  }

  function isAdminUrl(url) {
    try { return new URL(url, location.origin).pathname.indexOf('/admin/') === 0; }
    catch (e) { return false; }
  }

  var _fetch = window.fetch.bind(window);
  window.fetch = function (input, init) {
    init = init || {};
    var url = (typeof input === 'string') ? input : (input && input.url) || '';
    var admin = isAdminUrl(url);
    if (admin) {
      var tok = askToken();  // usa quello salvato, o chiede una volta (guarded)
      var headers = new Headers(
        init.headers || (typeof input !== 'string' && input && input.headers) || {}
      );
      if (tok) headers.set('X-Admin-Token', tok);
      init.headers = headers;
    }
    return _fetch(input, init).then(function (res) {
      if (admin && res.status === 401) {
        // token assente/errato: ripulisci e — se non già rifiutato in questa
        // sessione — richiedi una volta. NESSUN reload, e `declined` non viene
        // resettato → niente loop/tempesta di prompt con auto-refresh.
        clearToken();
        askToken();
      }
      return res;
    });
  };

  // Prompt eager una volta al load (best-effort): così l'utente inserisce il
  // token prima ancora delle chiamate della pagina. Il wrapper è già installato.
  askToken();
})();
