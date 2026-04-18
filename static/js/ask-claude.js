// ═══════════════════════════════════════════════════════════════════
// AtlasPI — "Ask Claude" module (v6.50)
//
// Binds the header button #ask-claude-btn to:
//   1. Build a context-aware prompt based on what's currently selected
//      (entity detail open? year being viewed? filters active?)
//   2. Copy that prompt to clipboard + open claude.ai in new tab
//   3. Show a toast confirming the prompt was copied
//
// Why copy-to-clipboard + open, not URL param?
//   claude.ai doesn't support `?q=` / `?prompt=` query param for prefill.
//   User paste is the robust pattern. Toast tells them what to do.
// ═══════════════════════════════════════════════════════════════════

(function() {
  'use strict';

  const CLAUDE_URL = 'https://claude.ai/new';

  function buildPrompt() {
    // Gather current app state (defensively — may be undefined in other pages).
    const year = (typeof state !== 'undefined' && state && state.year)
      ? state.year
      : (document.getElementById('year-input')?.value || null);
    const selectedEntityId = (typeof state !== 'undefined' && state && state.entity)
      ? state.entity : null;
    const selectedEntity = (selectedEntityId && typeof detailCache !== 'undefined' && detailCache[selectedEntityId])
      ? detailCache[selectedEntityId]
      : null;

    const apiBase = location.origin;
    const lines = [];

    if (selectedEntity) {
      lines.push(`I'm looking at the historical entity "${selectedEntity.name_original}" in AtlasPI.`);
      lines.push('');
      lines.push(`- Period: ${selectedEntity.year_start} → ${selectedEntity.year_end ?? 'ongoing'}`);
      if (selectedEntity.entity_type) lines.push(`- Type: ${selectedEntity.entity_type}`);
      if (selectedEntity.capital && selectedEntity.capital.name) {
        lines.push(`- Capital: ${selectedEntity.capital.name}`);
      }
      lines.push('');
      lines.push(`Full data: ${apiBase}/v1/entities/${selectedEntity.id}`);
      lines.push('');
      lines.push('Please:');
      lines.push('1. Give me a narrative overview of this entity');
      lines.push('2. Explain the main events of its history');
      lines.push('3. Note any ethical / contested aspects (conquests, rebrandings, slavery, etc.)');
      lines.push('4. Compare it with 1-2 contemporary powers of the same era');
      lines.push('');
      lines.push(`You can also query the AtlasPI API:`);
      lines.push(`- ${apiBase}/v1/entities/${selectedEntity.id}/events — events linked`);
      lines.push(`- ${apiBase}/v1/entities/${selectedEntity.id}/successors — chain successors`);
      lines.push(`- ${apiBase}/v1/snapshot/year/${selectedEntity.year_start} — world at founding`);
    } else if (year) {
      lines.push(`I'm exploring the world in year ${year} using AtlasPI.`);
      lines.push('');
      lines.push(`Snapshot: ${apiBase}/v1/snapshot/year/${year}`);
      lines.push('');
      lines.push('Please:');
      lines.push('1. Give me a narrative summary of this era globally (not just Europe)');
      lines.push('2. List the most powerful / influential polities of this year');
      lines.push('3. Highlight one under-told story from outside the usual Western focus');
      lines.push('4. Note ongoing historical processes (rise/decline of specific empires, etc.)');
    } else {
      lines.push('I want to explore historical geography using AtlasPI.');
      lines.push('');
      lines.push(`Database: ${apiBase}/v1/stats`);
      lines.push(`Docs: ${apiBase}/docs`);
      lines.push('');
      lines.push('Help me pick an interesting era to start exploring.');
    }

    lines.push('');
    lines.push(`---`);
    // v6.66: i numeri sono letti da window.i18nVars (popolati a runtime da
    // hydrateLiveStats() in app.js). Fallback statici solo se la fetch /health
    // fallisce — meglio mostrare un numero "abbastanza recente" che uno rotto.
    const v = (window.i18nVars || {});
    const nEnt = v.entities || '1,034';
    const nEvt = v.events || '643';
    const nRul = v.rulers || '105';
    const nSit = v.sites || '1,249';
    const nLng = v.languages || '29';
    lines.push(`AtlasPI is a free public REST API with ${nEnt} historical entities, ${nEvt} events, ${nRul} rulers, ${nSit} archaeological sites, and ${nLng} historical languages. Native-script names, academic sources, ETHICS layer.`);

    return lines.join('\n');
  }

  async function handleAskClaude() {
    const prompt = buildPrompt();
    try {
      await navigator.clipboard.writeText(prompt);
      if (typeof showToast === 'function') {
        showToast(window.t('claude_prompt_copied'));
      }
    } catch (err) {
      // Fallback: silent — still open claude, user types manually
      console.warn('Clipboard copy failed:', err);
    }
    // Open claude.ai in new tab.
    window.open(CLAUDE_URL, '_blank', 'noopener,noreferrer');
  }

  window.askClaude = handleAskClaude;

  // Bind on DOMContentLoaded (or immediately if already loaded)
  function init() {
    const btn = document.getElementById('ask-claude-btn');
    if (btn) btn.addEventListener('click', handleAskClaude);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
