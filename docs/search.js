
let searchIndex = null;

async function loadIndex() {
  if (searchIndex) return;
  try {
    const [baseRes, manualRes] = await Promise.all([
      fetch('search-index.json'),
      fetch('manual-articles.json')
    ]);
    const base = await baseRes.json();
    const raw = await manualRes.json();
    const manuals = raw.map(a => ({
      title: a.title,
      url: a.blog + '/' + a.file,
      blog: a.blogName,
      date: a.date,
      cats: a.category
    }));
    searchIndex = [...manuals, ...base];
  } catch(e) {
    try {
      const res = await fetch('search-index.json');
      searchIndex = await res.json();
    } catch(e2) { searchIndex = []; }
  }
}

async function doSearch(q) {
  await loadIndex();
  const query = q.toLowerCase().trim();
  if (!query) return [];
  return searchIndex.filter(item =>
    item.title.toLowerCase().includes(query) ||
    (item.cats && item.cats.toLowerCase().includes(query))
  );
}

document.addEventListener('DOMContentLoaded', function() {
  const input = document.getElementById('search-input');
  const results = document.getElementById('search-results');
  const resultCount = document.getElementById('result-count');

  if (!input || !results) return;

  let timer;
  input.addEventListener('input', function() {
    clearTimeout(timer);
    const q = this.value;
    timer = setTimeout(async function() {
      if (!q.trim()) {
        results.innerHTML = '';
        if (resultCount) resultCount.textContent = '';
        return;
      }
      const hits = await doSearch(q);
      if (resultCount) resultCount.textContent = hits.length + '件';
      if (hits.length === 0) {
        results.innerHTML = '<p style="color:#64748b;padding:20px 0">記事が見つかりませんでした</p>';
        return;
      }
      results.innerHTML = hits.slice(0, 50).map(item => `
        <a href="${item.url}" class="result-item" style="display:block;text-decoration:none">
          <div class="ri-title">${item.title}</div>
          <div class="ri-meta">${item.blog} &nbsp;·&nbsp; ${item.date} &nbsp;·&nbsp; ${item.cats}</div>
        </a>
      `).join('');
    }, 200);
  });

  // Header search redirect
  document.querySelectorAll('.site-search input').forEach(el => {
    el.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' && this.value.trim()) {
        const isRoot = !location.pathname.split('/').slice(-2, -1)[0].match(/^[a-z]/);
        const base = isRoot ? 'search.html' : '../search.html';
        location.href = base + '?q=' + encodeURIComponent(this.value.trim());
      }
    });
  });

  // Auto-fill from URL param
  const urlQ = new URLSearchParams(location.search).get('q');
  if (urlQ && input) {
    input.value = urlQ;
    input.dispatchEvent(new Event('input'));
  }
});
