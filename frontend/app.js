const form = document.getElementById('bbox-form');
const statusEl = document.getElementById('status');
const scoreEl = document.getElementById('score');
const camerasEl = document.getElementById('cameras');
const eventsEl = document.getElementById('events');

async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed: ${res.status}`);
  return res.json();
}

function renderList(el, items, mapFn) {
  el.innerHTML = '';
  for (const item of items) {
    const li = document.createElement('li');
    li.textContent = mapFn(item);
    el.appendChild(li);
  }
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const data = new FormData(form);
  const params = new URLSearchParams(data);
  statusEl.textContent = 'Loading...';

  try {
    const [cameras, events, summary] = await Promise.all([
      fetchJSON(`/api/cameras?${params}`),
      fetchJSON(`/api/events?${params}`),
      fetchJSON('/api/aoi/summary?name=Live%20AOI'),
    ]);

    renderList(camerasEl, cameras, (c) => `${c.name} (${c.lat.toFixed(3)}, ${c.lon.toFixed(3)})`);
    renderList(eventsEl, events, (evt) => `${evt.category.toUpperCase()}: ${evt.title}`);

    scoreEl.textContent = `${summary.headline} — score ${summary.situation_score}`;
    statusEl.textContent = JSON.stringify(
      {
        cameras: cameras.length,
        events: events.length,
        factors: summary.factors,
      },
      null,
      2,
    );
  } catch (err) {
    statusEl.textContent = `Error: ${err.message}`;
  }
});
