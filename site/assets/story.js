const endpoint = (await fetch('../../data/config.json').then(r => r.json()).catch(() => ({}))).feedbackEndpoint || '';
const form = document.querySelector('.feedback');
if (form) form.addEventListener('submit', async event => {
  event.preventDefault();
  const output = form.querySelector('output');
  const values = Object.fromEntries(new FormData(form));
  const payload = { story_id: form.dataset.story, version: form.dataset.version, comment: values.comment, scores: { feeling: Number(values.feeling), story_fit: Number(values.story_fit), sample_quality: Number(values.sample_quality) } };
  if (!endpoint) { output.textContent = 'Endpoint raportów nie jest jeszcze skonfigurowany.'; return; }
  output.textContent = 'Wysyłanie…';
  try { const response = await fetch(endpoint, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)}); const result = await response.json(); output.textContent = response.ok ? `Raport wysłany: ${result.issue_url}` : `Błąd: ${result.error || 'nieznany'}`; } catch { output.textContent = 'Nie udało się wysłać raportu.'; }
});
