const LOCAL_KEY = 'jingleRatings';
function loadLocalRatings() {
  try { return JSON.parse(localStorage.getItem(LOCAL_KEY) || '{}'); } catch { return {}; }
}
const localStore = loadLocalRatings();
// Device-local ratings bridge the gap until the sync workflow republishes
// data/versions.json: the homepage must reflect freshly submitted scores.
function localBest(id) {
  let bestLocal = null;
  for (const [key, entry] of Object.entries(localStore)) {
    if (!key.startsWith(`${id}:`) || !Number.isFinite(entry && entry.total)) continue;
    if (bestLocal === null || entry.total > bestLocal) bestLocal = entry.total;
  }
  return bestLocal;
}

const state = { stories: [], config: { feedbackEndpoint: '' } };
const $ = selector => document.querySelector(selector);

function latest(story) { return story.latest_at || story.versions?.at(-1)?.created_at || ''; }
function best(story) { const scores = (story.versions || []).map(v => v.score).filter(Number.isFinite); return scores.length ? Math.max(...scores) : null; }
function hasRating(story) { return (story.versions || []).some(v => Number.isFinite(v.score)); }
function combinedBest(story) {
  const remote = best(story); const local = localBest(story.id);
  if (remote === null) return local;
  if (local === null) return remote;
  return Math.max(remote, local);
}
function hasAnyRating(story) { return hasRating(story) || localBest(story.id) !== null; }
// Polska odmiana: 1 wersja · 2-4 (poza 12-14) wersje · pozostałe wersji.
function pluralWersje(count) {
  if (count === 1) return 'wersja';
  const mod10 = count % 10, mod100 = count % 100;
  return (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) ? 'wersje' : 'wersji';
}
// Dopełniacz po „z": 1 z 1 fabuły · 2 z 5 fabuł.
function pluralFabul(count) { return count === 1 ? 'fabuły' : 'fabuł'; }
function versionNumber(version) { const n = Number(String(version?.label || '').replace(/^v/, '')); return Number.isFinite(n) ? n : 0; }
function isVersionRated(story, version) {
  if (Number.isFinite(version?.score)) return true;
  const entry = localStore[`${story.id}:${version.label}`];
  return Boolean(entry && Number.isFinite(entry.total));
}
// "New unrated version": a version newer than the newest rated one is still
// waiting for a score. The owner should spot it next to the best-rating badge.
function hasUnratedNewVersion(story) {
  const versions = story.versions || [];
  const rated = versions.filter(v => isVersionRated(story, v));
  if (!rated.length) return false;
  const newestRated = Math.max(...rated.map(versionNumber));
  return versions.some(v => versionNumber(v) > newestRated && !isVersionRated(story, v));
}

function render() {
  const query = ($('#search').value || '').toLowerCase().trim();
  const filtered = state.stories.filter(story => !query || [story.id, story.title].join(' ').toLowerCase().includes(query));
  const stories = filtered.sort((a, b) => {
    const unrated = Number(!hasAnyRating(a)) - Number(!hasAnyRating(b));
    if (unrated) return -unrated;
    const scoreDifference = (combinedBest(a) ?? -1) - (combinedBest(b) ?? -1);
    return scoreDifference || latest(b).localeCompare(latest(a));
  });
  const freshCount = stories.filter(hasUnratedNewVersion).length;
  $('#summary').textContent = `${stories.length} z ${state.stories.length} ${pluralFabul(state.stories.length)} · nieocenione są na górze${freshCount ? ` · ${freshCount} z nową nieocenioną wersją` : ''}`;
  $('#catalog').innerHTML = stories.map(story => {
    const remote = best(story);
    const rating = combinedBest(story);
    const localOnly = rating !== null && remote === null;
    const versions = story.versions?.length || 0;
    const versionLabel = pluralWersje(versions);
    const status = rating === null ? 'nieocenione' : `najlepiej ${rating}/15${localOnly ? ' · na tym urządzeniu' : ''}`;
    const freshBadge = hasUnratedNewVersion(story) ? '<span class="pill fresh" title="Nowsza wersja tej fabuły czeka na ocenę">nieoceniona nowa wersja</span>' : '';
    return `<article class="story"><div class="story-head"><h2><a href="stories/${story.id}/"><span class="story-id">#${story.id}</span> ${story.title}</a></h2><div class="badges"><span class="pill ${rating === null ? 'wait' : 'good'}">${status}</span>${freshBadge}</div></div><div class="meta"><span class="pill">${versions} ${versionLabel}</span><span class="pill">${rating === null ? 'oczekuje na ocenę' : localOnly ? 'ocenione lokalnie' : 'ma ocenę'}</span></div></article>`;
  }).join('') || '<p class="lede">Brak wyników.</p>';
}

Promise.all([fetch('data/catalog.json').then(r => r.json()), fetch('data/config.json').then(r => r.json()).catch(() => ({}))]).then(([data, config]) => { state.stories = data.stories || []; state.config = config; render(); }).catch(() => { $('#catalog').innerHTML = '<p class="lede">Nie udało się wczytać katalogu.</p>'; });
$('#search').addEventListener('input', render);
