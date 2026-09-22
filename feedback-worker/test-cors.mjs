import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const source = await readFile(new URL('./src/index.js', import.meta.url), 'utf8');
const { default: worker } = await import(`data:text/javascript,${encodeURIComponent(source)}`);
const env = { GITHUB_REPOSITORY: 'szybkoiwyraznie-rgb/mtgdatabase' };

async function preflight(origin) {
  const request = new Request('https://worker.example.invalid', {
    method: 'OPTIONS',
    headers: { Origin: origin },
  });
  return worker.fetch(request, env);
}

const projectPages = await preflight('https://szybkoiwyraznie-rgb.github.io');
assert.equal(projectPages.status, 204);
assert.equal(projectPages.headers.get('Access-Control-Allow-Origin'), 'https://szybkoiwyraznie-rgb.github.io');

const unrelatedPages = await preflight('https://unrelated.github.io');
assert.equal(unrelatedPages.status, 204);
assert.equal(unrelatedPages.headers.get('Access-Control-Allow-Origin'), null);

const nullOrigin = await preflight('null');
assert.equal(nullOrigin.headers.get('Access-Control-Allow-Origin'), null);

console.log('OK  worker CORS permits only the configured repository owner Pages origin');
