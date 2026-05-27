/* AtlasPI Feedback Widget — Phase G1 (v6.99.75)
 *
 * Aggiunge un bottone "Segnala / Suggest correction" al detail panel
 * (#detail-content) e apre un modal per sottomettere feedback via
 * POST /v1/feedback.
 *
 * Self-contained: niente dipendenze, niente modifiche ad app.js.
 * Hook: MutationObserver su #detail-content. Quando il contenuto cambia
 * e contiene un'entita'/evento/citta', inietta il bottone in fondo.
 */
(function () {
  'use strict';

  const API_BASE = window.location.origin;
  const CATEGORIES = [
    { value: 'incorrect_data', label_it: 'Dato errato', label_en: 'Incorrect data' },
    { value: 'missing_source', label_it: 'Fonte mancante', label_en: 'Missing source' },
    { value: 'bias_report', label_it: 'Bias / rappresentazione', label_en: 'Bias / representation' },
    { value: 'boundary_dispute', label_it: 'Confini imprecisi', label_en: 'Imprecise boundary' },
    { value: 'missing_entity', label_it: 'Entità mancante', label_en: 'Missing entity' },
    { value: 'translation_error', label_it: 'Errore traduzione', label_en: 'Translation error' },
    { value: 'ethics_concern', label_it: 'Concern etico', label_en: 'Ethics concern' },
    { value: 'other', label_it: 'Altro', label_en: 'Other' },
  ];

  const lang = (document.documentElement.lang || 'it').toLowerCase().startsWith('en') ? 'en' : 'it';
  const L = {
    it: {
      btn: '🚩 Segnala / Suggerisci correzione',
      title: 'Suggerisci una correzione',
      intro: 'Aiuta a migliorare AtlasPI. La review umana è sempre richiesta prima di applicare modifiche ai contenuti storici.',
      category: 'Categoria',
      field_name: 'Campo (opzionale)',
      field_help: 'es. year_end, boundary_geojson, name_original',
      current_value: 'Valore attuale (opzionale)',
      suggested_value: 'Valore corretto proposto',
      citation: 'Fonte / citation (raccomandato)',
      citation_help: 'es. "Holt 1970, p. 142" o ISBN/DOI',
      reasoning: 'Spiegazione (1-3 frasi)',
      submitter_id: 'Email o handle (opzionale)',
      submitter_id_help: 'Lasciato vuoto: feedback anonimo. Email "ac.uk/.edu/etc" trattata come accademica.',
      submit: 'Invia feedback',
      cancel: 'Annulla',
      submitting: 'Invio in corso…',
      ok: '✅ Feedback inviato! ID #',
      err: '❌ Errore: ',
      ethics_note: 'Per cambiamenti che toccano nomi originali, conquiste, rappresentazione di popoli o confini contestati, la review umana è obbligatoria (ETHICS-001–010).',
    },
    en: {
      btn: '🚩 Report / Suggest correction',
      title: 'Suggest a correction',
      intro: 'Help improve AtlasPI. Human review is always required before applying changes to historical content.',
      category: 'Category',
      field_name: 'Field (optional)',
      field_help: 'e.g. year_end, boundary_geojson, name_original',
      current_value: 'Current value (optional)',
      suggested_value: 'Suggested value',
      citation: 'Source / citation (recommended)',
      citation_help: 'e.g. "Holt 1970, p. 142" or ISBN/DOI',
      reasoning: 'Explanation (1-3 sentences)',
      submitter_id: 'Email or handle (optional)',
      submitter_id_help: 'Leave blank for anonymous feedback. Academic emails (.edu, .ac.uk) are treated as verified.',
      submit: 'Submit feedback',
      cancel: 'Cancel',
      submitting: 'Submitting…',
      ok: '✅ Feedback submitted! ID #',
      err: '❌ Error: ',
      ethics_note: 'Changes touching original names, conquests, representation of peoples, or contested borders require human review (ETHICS-001–010).',
    },
  }[lang];

  // ─── Style injection ────────────────────────────────────────────
  const css = `
    .apfb-btn-container { margin-top: 16px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.08); }
    .apfb-btn {
      width: 100%; padding: 8px 14px; cursor: pointer;
      background: transparent; border: 1px solid rgba(255,200,150,0.4);
      color: rgba(255,200,150,0.9); border-radius: 4px;
      font-size: 0.85em; font-family: inherit;
      transition: all 0.15s ease;
    }
    .apfb-btn:hover { background: rgba(255,200,150,0.08); border-color: rgba(255,200,150,0.7); color: rgba(255,200,150,1); }
    .apfb-overlay {
      position: fixed; inset: 0; background: rgba(0,0,0,0.7);
      display: flex; align-items: center; justify-content: center;
      z-index: 9999; padding: 16px;
    }
    .apfb-modal {
      background: #1a1b1e; border: 1px solid #2a2b2e;
      border-radius: 8px; padding: 22px;
      max-width: 540px; width: 100%;
      max-height: 90vh; overflow-y: auto;
      color: #e6e6e6; font-family: inherit;
    }
    .apfb-modal h2 { margin: 0 0 6px; font-size: 1.15em; color: rgba(255,200,150,0.95); }
    .apfb-modal p.intro { font-size: 0.82em; color: #9aa1a8; margin: 0 0 16px; line-height: 1.5; }
    .apfb-modal label { display: block; margin: 12px 0 4px; font-size: 0.8em; color: #c8cdd3; }
    .apfb-modal label .hint { color: #6e7480; font-size: 0.85em; font-weight: 400; }
    .apfb-modal input, .apfb-modal select, .apfb-modal textarea {
      width: 100%; padding: 7px 10px; box-sizing: border-box;
      background: #0f1012; border: 1px solid #2a2b2e; border-radius: 4px;
      color: #e6e6e6; font-size: 0.85em; font-family: inherit;
    }
    .apfb-modal textarea { resize: vertical; min-height: 60px; }
    .apfb-modal .ethics-box {
      background: rgba(200,150,80,0.08); border-left: 3px solid rgba(255,200,150,0.6);
      padding: 8px 12px; font-size: 0.78em; color: #b9b0a0; margin: 14px 0; line-height: 1.5;
    }
    .apfb-modal .actions { display: flex; gap: 8px; margin-top: 18px; justify-content: flex-end; }
    .apfb-modal button { padding: 8px 16px; cursor: pointer; border-radius: 4px; font-size: 0.85em; font-family: inherit; border: 1px solid #2a2b2e; }
    .apfb-modal button.primary { background: rgba(255,200,150,0.15); color: rgba(255,200,150,1); border-color: rgba(255,200,150,0.4); }
    .apfb-modal button.primary:hover { background: rgba(255,200,150,0.25); }
    .apfb-modal button.primary:disabled { opacity: 0.5; cursor: not-allowed; }
    .apfb-modal button.cancel { background: transparent; color: #9aa1a8; }
    .apfb-modal button.cancel:hover { background: #2a2b2e; color: #e6e6e6; }
    .apfb-status { font-size: 0.85em; margin-top: 8px; padding: 8px 12px; border-radius: 4px; }
    .apfb-status.ok { background: rgba(80,200,120,0.12); color: rgba(120,220,150,0.95); }
    .apfb-status.err { background: rgba(220,80,80,0.12); color: rgba(255,140,140,0.95); }
  `;
  const styleEl = document.createElement('style');
  styleEl.textContent = css;
  document.head.appendChild(styleEl);

  // ─── Helpers ────────────────────────────────────────────────────
  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function currentTargetIds() {
    // Inspect the URL hash or detail panel headings to figure out
    // what entity/event/city is currently displayed.
    // Heuristic: look for "entity-id" data attribute or H2 text patterns.
    const content = document.getElementById('detail-content');
    if (!content) return {};

    // Look for data-entity-id, data-event-id, data-city-id attributes
    // on any element inside the detail content.
    const ent = content.querySelector('[data-entity-id]');
    if (ent) return { entity_id: parseInt(ent.dataset.entityId, 10) };
    const ev = content.querySelector('[data-event-id]');
    if (ev) return { event_id: parseInt(ev.dataset.eventId, 10) };
    const ci = content.querySelector('[data-city-id]');
    if (ci) return { city_id: parseInt(ci.dataset.cityId, 10) };

    // Fallback: parse from URL hash if it looks like #entity/123
    const m = (location.hash || '').match(/(entity|event|city)\/(\d+)/);
    if (m) {
      const key = m[1] + '_id';
      return { [key]: parseInt(m[2], 10) };
    }

    // Fallback final: inspect global state if exposed
    if (window.currentEntityId) return { entity_id: window.currentEntityId };
    if (window.currentDetailEntity && window.currentDetailEntity.id) {
      return { entity_id: window.currentDetailEntity.id };
    }
    return {};
  }

  function buildModalHtml(targetIds) {
    const optsHtml = CATEGORIES.map(c => {
      const label = lang === 'en' ? c.label_en : c.label_it;
      return `<option value="${c.value}">${label}</option>`;
    }).join('');

    const targetLine = (() => {
      if (targetIds.entity_id) return `<div style="font-size:0.78em;color:#6e7480;margin-bottom:8px">Target: entity_id=${targetIds.entity_id}</div>`;
      if (targetIds.event_id) return `<div style="font-size:0.78em;color:#6e7480;margin-bottom:8px">Target: event_id=${targetIds.event_id}</div>`;
      if (targetIds.city_id) return `<div style="font-size:0.78em;color:#6e7480;margin-bottom:8px">Target: city_id=${targetIds.city_id}</div>`;
      return '';
    })();

    return `
      <div class="apfb-modal" role="dialog" aria-modal="true" aria-labelledby="apfb-title">
        <h2 id="apfb-title">${L.title}</h2>
        <p class="intro">${L.intro}</p>
        ${targetLine}
        <form id="apfb-form">
          <label>${L.category}
            <select name="category" required>${optsHtml}</select>
          </label>
          <label>${L.field_name} <span class="hint">${L.field_help}</span>
            <input type="text" name="field_name" maxlength="64">
          </label>
          <label>${L.current_value}
            <textarea name="current_value" rows="2"></textarea>
          </label>
          <label>${L.suggested_value}
            <textarea name="suggested_value" rows="2"></textarea>
          </label>
          <label>${L.citation} <span class="hint">${L.citation_help}</span>
            <textarea name="citation" rows="2"></textarea>
          </label>
          <label>${L.reasoning}
            <textarea name="reasoning" rows="2"></textarea>
          </label>
          <label>${L.submitter_id} <span class="hint">${L.submitter_id_help}</span>
            <input type="text" name="submitter_id" maxlength="256">
          </label>
          <div class="ethics-box">${L.ethics_note}</div>
          <div id="apfb-status-slot"></div>
          <div class="actions">
            <button type="button" class="cancel" id="apfb-cancel">${L.cancel}</button>
            <button type="submit" class="primary" id="apfb-submit">${L.submit}</button>
          </div>
        </form>
      </div>
    `;
  }

  function openModal() {
    const targetIds = currentTargetIds();
    const overlay = document.createElement('div');
    overlay.className = 'apfb-overlay';
    overlay.innerHTML = buildModalHtml(targetIds);
    document.body.appendChild(overlay);

    function close() {
      overlay.remove();
    }
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) close();
    });
    document.getElementById('apfb-cancel').addEventListener('click', close);

    const form = document.getElementById('apfb-form');
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const fd = new FormData(form);
      const payload = {
        category: fd.get('category'),
        submitter_type: fd.get('submitter_id') ? 'human' : 'anonymous',
        submitter_id: fd.get('submitter_id') || null,
        field_name: fd.get('field_name') || null,
        current_value: fd.get('current_value') || null,
        suggested_value: fd.get('suggested_value') || null,
        citation: fd.get('citation') || null,
        reasoning: fd.get('reasoning') || null,
        ...targetIds,
      };

      const statusEl = document.getElementById('apfb-status-slot');
      const submitBtn = document.getElementById('apfb-submit');
      statusEl.innerHTML = `<div class="apfb-status">${L.submitting}</div>`;
      submitBtn.disabled = true;

      try {
        const res = await fetch(`${API_BASE}/v1/feedback`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.detail || `HTTP ${res.status}`);
        }
        statusEl.innerHTML = `<div class="apfb-status ok">${L.ok}${data.id}</div>`;
        setTimeout(close, 2000);
      } catch (err) {
        statusEl.innerHTML = `<div class="apfb-status err">${L.err}${esc(err.message)}</div>`;
        submitBtn.disabled = false;
      }
    });

    // Keyboard ESC closes
    document.addEventListener('keydown', function escHandler(e) {
      if (e.key === 'Escape') {
        close();
        document.removeEventListener('keydown', escHandler);
      }
    });
  }

  // ─── Button injection ───────────────────────────────────────────
  function injectButton() {
    const content = document.getElementById('detail-content');
    if (!content) return;
    if (content.querySelector('.apfb-btn-container')) return; // already injected
    // Only inject if content has actual data (not spinner)
    if (content.querySelector('.detail-spinner')) return;
    if (content.querySelector('.placeholder')) return;
    // Only if there's an h2 (entity/event/city rendered)
    if (!content.querySelector('h2')) return;

    const container = document.createElement('div');
    container.className = 'apfb-btn-container';
    const btn = document.createElement('button');
    btn.className = 'apfb-btn';
    btn.type = 'button';
    btn.textContent = L.btn;
    btn.addEventListener('click', openModal);
    container.appendChild(btn);
    content.appendChild(container);
  }

  // Watch for detail content changes
  function startObserver() {
    const content = document.getElementById('detail-content');
    if (!content) {
      setTimeout(startObserver, 500);
      return;
    }
    const obs = new MutationObserver(() => {
      // Debounce: wait next tick
      setTimeout(injectButton, 50);
    });
    obs.observe(content, { childList: true, subtree: true });
    // Initial check
    injectButton();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startObserver);
  } else {
    startObserver();
  }
})();
