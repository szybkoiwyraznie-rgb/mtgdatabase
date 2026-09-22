const LOCAL_KEY = 'jingleRatings';
const loadLocal = () => { try { return JSON.parse(localStorage.getItem(LOCAL_KEY) || '{}'); } catch { return {}; } };
const saveLocal = data => localStorage.setItem(LOCAL_KEY, JSON.stringify(data));

function applyBadge(form, total, note) {
  const card = form.closest('section.version');
  const badge = card && card.querySelector('.version-head small');
  if (badge) badge.textContent = `${total}/15${note ? ' · ' + note : ''}`;
}

// Ratings are shown instantly from this device's cache; the automatic sync
// (feedback issue -> workflow -> data/versions.json -> Pages rebuild) makes
// them permanent for everyone within a couple of minutes.
const stored = loadLocal();
document.querySelectorAll('.feedback').forEach(form => {
  const entry = stored[`${form.dataset.story}:${form.dataset.version}`];
  if (entry && Number.isFinite(entry.total)) applyBadge(form, entry.total, 'na tym urządzeniu');
});

const endpoint = (await fetch('../../data/config.json').then(r => r.json()).catch(() => ({}))).feedbackEndpoint || '';
document.querySelectorAll('.feedback').forEach(form => form.addEventListener('submit', async event => {
  event.preventDefault();
  const output = form.querySelector('output');
  const values = Object.fromEntries(new FormData(form));
  const payload = { story_id: form.dataset.story, version: form.dataset.version, comment: values.comment || '', scores: { feeling: Number(values.feeling), story_fit: Number(values.story_fit), sample_quality: Number(values.sample_quality) } };
  if (!endpoint) { output.textContent = 'Endpoint raportów nie jest jeszcze skonfigurowany.'; return; }
  output.textContent = 'Wysyłanie…';
  try {
    const response = await fetch(endpoint, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)});
    const result = await response.json();
    if (response.ok) {
      const total = payload.scores.feeling + payload.scores.story_fit + payload.scores.sample_quality;
      const data = loadLocal();
      data[`${payload.story_id}:${payload.version}`] = { ...payload.scores, total, comment: String(payload.comment || ''), at: new Date().toISOString() };
      saveLocal(data);
      applyBadge(form, total, 'na tym urządzeniu');
      output.textContent = `Raport wysłany (${total}/15): ${result.issue_url} — synchronizacja zaktualizuje stronę w ciągu kilku minut.`;
    } else {
      output.textContent = `Błąd: ${result.error || 'nieznany'}`;
    }
  } catch { output.textContent = 'Nie udało się wysłać raportu.'; }
}));
