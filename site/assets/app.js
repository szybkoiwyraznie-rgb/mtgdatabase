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

function render() {
  const query = ($('#search').value || '').toLowerCase().trim();
  const filtered = state.stories.filter(story => !query || [story.id, story.title].join(' ').toLowerCase().includes(query));
  const stories = filtered.sort((a, b) => {
    const unrated = Number(!hasAnyRating(a)) - Number(!hasAnyRating(b));
    if (unrated) return -unrated;
    const scoreDifference = (combinedBest(a) ?? -1) - (combinedBest(b) ?? -1);
    return scoreDifference || latest(b).localeCompare(latest(a));
  });
  $('#summary').textContent = `${stories.length} z ${state.stories.length} fabuł · nieocenione są na górze`;
  $('#catalog').innerHTML = stories.map(story => {
    const remote = best(story);
    const rating = combinedBest(story);
    const localOnly = rating !== null && remote === null;
    const versions = story.versions?.length || 0;
    const versionLabel = versions === 1 ? 'wersja' : 'wersji';
    const status = rating === null ? 'nieocenione' : `najlepiej ${rating}/15${localOnly ? ' · na tym urządzeniu' : ''}`;
    return `<article class="story"><div class="story-head"><h2><a href="stories/${story.id}/"><span class="story-id">#${story.id}</span> ${story.title}</a></h2><span class="pill ${rating === null ? 'wait' : 'good'}">${status}</span></div><div class="meta"><span class="pill">${versions} ${versionLabel}</span><span class="pill">${rating === null ? 'oczekuje na ocenę' : localOnly ? 'ocenione lokalnie' : 'ma ocenę'}</span></div></article>`;
  }).join('') || '<p class="lede">Brak wyników.</p>';
}

Promise.all([fetch('data/catalog.json').then(r => r.json()), fetch('data/config.json').then(r => r.json()).catch(() => ({}))]).then(([data, config]) => { state.stories = data.stories || []; state.config = config; render(); }).catch(() => { $('#catalog').innerHTML = '<p class="lede">Nie udało się wczytać katalogu.</p>'; });
$('#search').addEventListener('input', render);
