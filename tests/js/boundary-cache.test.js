/* Wave 2.6 (audit #8): copertura automatica della logica di merge del
 * lazy-loader boundary (Wave 1.3) — la parte più complessa e a rischio del
 * frontend (concorrenza/merge), prima senza alcun test. Gira con `node --test`.
 */
'use strict';
const test = require('node:test');
const assert = require('node:assert');
const { mergeBoundaryBatch } = require('../../static/js/boundary-cache.js');

function entity(id, extra = {}) {
  return { id, name_original: `name-${id}`, status: 'confirmed', year_start: 1000, confidence_score: 0.9, ...extra };
}

test('merges boundary_geojson onto matching entities and returns count', () => {
  const all = [entity(1), entity(2), entity(3)];
  const merged = mergeBoundaryBatch(all, [
    { id: 1, boundary_geojson: '{"a":1}' },
    { id: 3, boundary_geojson: '{"b":2}' },
  ]);
  assert.strictEqual(merged, 2);
  assert.strictEqual(all[0].boundary_geojson, '{"a":1}');
  assert.strictEqual(all[0]._boundary_load_state, 'loaded');
  assert.strictEqual(all[2].boundary_geojson, '{"b":2}');
  assert.strictEqual(all[1].boundary_geojson, undefined); // id 2 non nel batch
});

test('does NOT overwrite canonical fields (name/status/year/confidence)', () => {
  const all = [entity(1)];
  mergeBoundaryBatch(all, [{
    id: 1, boundary_geojson: '{}',
    name_original: 'WRONG', status: 'disputed', year_start: -999, confidence_score: 0.1,
  }]);
  assert.strictEqual(all[0].name_original, 'name-1');
  assert.strictEqual(all[0].status, 'confirmed');
  assert.strictEqual(all[0].year_start, 1000);
  assert.strictEqual(all[0].confidence_score, 0.9);
});

test('ignores batch entities not present in the canonical list', () => {
  const all = [entity(1)];
  const merged = mergeBoundaryBatch(all, [{ id: 999, boundary_geojson: '{}' }]);
  assert.strictEqual(merged, 0);
  assert.strictEqual(all.length, 1);
});

test('fills optional fields only when absent (no overwrite if already set)', () => {
  const all = [entity(1, { sources: ['keep'] }), entity(2)];
  mergeBoundaryBatch(all, [
    { id: 1, boundary_geojson: '{}', sources: ['new'], ethical_notes: 'x' },
    { id: 2, boundary_geojson: '{}', sources: ['fresh'] },
  ]);
  assert.deepStrictEqual(all[0].sources, ['keep']);   // già presente → non sovrascritto
  assert.strictEqual(all[0].ethical_notes, 'x');       // assente → riempito
  assert.deepStrictEqual(all[1].sources, ['fresh']);   // assente → riempito
});

test('is defensive against non-array input', () => {
  assert.strictEqual(mergeBoundaryBatch(null, []), 0);
  assert.strictEqual(mergeBoundaryBatch([], null), 0);
  assert.strictEqual(mergeBoundaryBatch(undefined, undefined), 0);
});
