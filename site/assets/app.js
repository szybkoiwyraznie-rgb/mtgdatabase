const state = { stories: [] };
const $ = (selector) => document.querySelector(selector);

function score(story) {
  const values = (story.versions || []).map(v => v.score).filter(Number.isFinite);
  return values.length ? Math.max(...values) : null;
}

function render() {
  const query = ($('#search').value || '').toLowerCase().trim();
  const stories = state.stories.filter(story =>
    !query || [story.id, story.title, story.story].join(' ').toLowerCase().includes(query)
  );
  $('#summary').textContent = `${stories.length} z ${state.stories.length} fabuł`;
  $('#catalog').innerHTML = stories.map(story => {
    const best = score(story);
    const versions = (story.versions || []).map(version => `
      <div class="version">
        <div><strong>${version.label}</strong><br><small>${version.score ? `${version.score}/15` : 'oczekuje na ocenę'}</small></div>
        <audio controls preload="none" src="${version.audio}"></audio>
      </div>`).join('');
    return `<article class="story">
      <div class="story-head"><h2><a href="stories/${story.id}/"><span class="story-id">#${story.id}</span> ${story.title}</a></h2><span class="pill ${best ? 'good' : 'wait'}">${best ? `najlepiej ${best}/15` : 'bez oceny'}</span></div>
      <p>${story.story}</p>
      <div class="meta"><span class="pill">${story.versions.length} wersji</span><span class="pill">${best ? 'ma ocenę' : 'nowy jingle'}</span></div>
      <details><summary>Odtwórz wersje</summary>${versions}</details>
    </article>`;
  }).join('') || '<p class="lede">Brak wyników.</p>';
}

Promise.all([fetch('data/catalog.json').then(response => response.json()), fetch('data/config.json').then(response => response.json()).catch(() => ({}))]).then(([data, config]) => { state.stories = data.stories || []; state.config = config; render(); }).catch(() => { $('#catalog').innerHTML = '<p class="lede">Nie udało się wczytać katalogu.</p>'; });
$('#search').addEventListener('input', render);
$('#catalog').addEventListener('submit', async (event) => { const form = event.target.closest('.feedback'); if (!form) return; event.preventDefault(); const output = form.querySelector('output'); if (!state.config.feedbackEndpoint) { output.textContent = 'Endpoint raportów nie jest jeszcze skonfigurowany.'; return; } const values = Object.fromEntries(new FormData(form)); const payload = { story_id: form.dataset.story, version: form.dataset.version, comment: values.comment, scores: { feeling: Number(values.feeling), story_fit: Number(values.story_fit), sample_quality: Number(values.sample_quality) } }; output.textContent = 'Wysyłanie…'; try { const response = await fetch(state.config.feedbackEndpoint, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) }); const result = await response.json(); output.textContent = response.ok ? `Raport wysłany: ${result.issue_url}` : `Błąd: ${result.error || 'nieznany'}`; } catch (error) { output.textContent = 'Nie udało się wysłać raportu.'; } });
