/**
 * Due Diligence Suite — Architectural Fitness Functions & Performance Budgets
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

test('Fitness 1: Presupuesto Estricto de Rendimiento en Web Suite', () => {
  const cssSize = fs.statSync(path.resolve('web/styles.css')).size;
  const htmlSize = fs.statSync(path.resolve('web/index.html')).size;
  const rumSize = fs.statSync(path.resolve('web/rumBeacon.js')).size;

  assert.ok(cssSize <= 60 * 1024, `web/styles.css excede 60 KB (${cssSize} B)`);
  assert.ok(htmlSize <= 60 * 1024, `web/index.html excede 60 KB (${htmlSize} B)`);
  assert.ok(rumSize <= 5 * 1024, `web/rumBeacon.js excede 5 KB (${rumSize} B)`);
});

test('Fitness 2: Auditoría Zero-Leakage y RUM Inyectado', () => {
  const html = fs.readFileSync(path.resolve('web/index.html'), 'utf8');
  assert.match(html, /rumBeacon\.js/, 'web/index.html debe cargar la baliza RUM');
  assert.doesNotMatch(html, /(?:sk_live|ghp_|AIza)[0-9a-zA-Z-_]{10,}/, 'web/index.html no debe exponer secretos');
});
