#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学習ポータル サイトジェネレーター
579記事 / 8ブログ を1サイトに統合
"""

import json, os, shutil, sys, io, re
from collections import defaultdict
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ============================================================
# CONFIGURATION
# ============================================================

_BASE     = os.path.dirname(os.path.abspath(__file__))
JSON_DIR  = os.path.join(_BASE, 'JSON')
OUT_DIR   = os.path.join(_BASE, 'docs')
SITE_NAME = '学習ポータル'

GROUPS = {
    'coding': {'name': 'Web コーディング', 'color': '#2563eb', 'light': '#eff6ff', 'border': '#bfdbfe'},
    'design': {'name': 'デザイン',          'color': '#7c3aed', 'light': '#f5f3ff', 'border': '#ddd6fe'},
    'review': {'name': '総合復習',           'color': '#059669', 'light': '#ecfdf5', 'border': '#a7f3d0'},
}

BLOGS = [
    {'file': 'blog_articles.json',                             'slug': 'web-hakubyo',       'name': 'Web白描',                         'group': 'coding', 'order': 1, 'emoji': '✏️',  'desc': 'HTML・CSS・Webリテラシーの基礎入門'},
    {'file': 'HTML_CSS__演習プロンプト__articles.json',        'slug': 'html-css-exercises', 'name': 'HTML/CSS 演習プロンプト',          'group': 'coding', 'order': 2, 'emoji': '💻', 'desc': 'HTML・CSSの演習問題と実践課題'},
    {'file': 'JavaScript_articles.json',                       'slug': 'javascript',         'name': 'JavaScript',                      'group': 'coding', 'order': 3, 'emoji': '⚡', 'desc': 'JavaScriptの基礎から応用まで'},
    {'file': 'JavaScript_演習プロンプト__articles.json',       'slug': 'js-exercises',       'name': 'JavaScript 演習プロンプト',        'group': 'coding', 'order': 4, 'emoji': '🎯', 'desc': 'JavaScriptの演習問題と実践課題'},
    {'file': 'Illustrator_基礎_articles.json',                 'slug': 'illustrator',        'name': 'Illustrator 基礎',                'group': 'design', 'order': 5, 'emoji': '🎨', 'desc': 'Adobe Illustratorの基礎と実践テクニック'},
    {'file': 'Photoshop_基礎_articles.json',                   'slug': 'photoshop',          'name': 'Photoshop 基礎',                  'group': 'design', 'order': 6, 'emoji': '🖼️', 'desc': 'Adobe Photoshopの基礎と画像編集技術'},
    {'file': 'Photoshop___Illusrator_実践演習_articles.json',  'slug': 'ps-ai-practice',     'name': 'Photoshop / Illustrator 実践演習', 'group': 'design', 'order': 7, 'emoji': '🏆', 'desc': 'Ps・Aiを活用した実践的なデザイン演習'},
    {'file': 'The_復習_articles.json',                         'slug': 'review',             'name': 'The 復習',                        'group': 'review', 'order': 8, 'emoji': '📚', 'desc': 'Web制作・デザイン全般の総復習'},
]

# ============================================================
# HELPERS
# ============================================================

# ============================================================
# IMAGE PATH PATCHING
# ============================================================

_image_map = None

def load_image_map():
    global _image_map
    if _image_map is not None:
        return _image_map
    map_path = os.path.join(_BASE, 'image-map.json')
    if os.path.exists(map_path):
        with open(map_path, encoding='utf-8') as f:
            _image_map = json.load(f)
        print(f'image-map.json 読み込み: {len(_image_map)}件')
    else:
        _image_map = {}
    return _image_map

def patch_images(html):
    """content_html内の画像URLをローカルパスに置換（articles/ から ../images/ へ）"""
    imap = load_image_map()
    if not imap:
        return html
    def replace_src(m):
        url = m.group(1)
        fname = imap.get(url)
        if fname:
            return f'src="../images/{fname}"'
        return m.group(0)
    return re.sub(r'src=["\']([^"\']+)["\']', replace_src, html)

def safe_filename(title):
    f = title + '.html'
    for ch in '\\/:*?"<>|':
        f = f.replace(ch, '_')
    return f

def strip_star(cat):
    return cat.lstrip('★')

def fmt_date(s):
    try:
        d = datetime.strptime(s[:10], '%Y-%m-%d')
        return f'{d.year}/{d.month:02d}/{d.day:02d}'
    except:
        return s

def get_cats(item):
    return [strip_star(c) for c in item.get('categories', []) if c != '★AI']

# ============================================================
# CSS (shared)
# ============================================================

SHARED_CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg: #f8fafc;
  --surface: #ffffff;
  --text: #1e293b;
  --muted: #64748b;
  --border: #e2e8f0;
  --radius: 10px;
  --shadow: 0 1px 3px rgba(0,0,0,.08), 0 1px 2px rgba(0,0,0,.04);
  --shadow-md: 0 4px 6px rgba(0,0,0,.06), 0 2px 4px rgba(0,0,0,.04);
  --font: 'Helvetica Neue', Arial, 'Hiragino Sans', 'Yu Gothic', sans-serif;
}

body { font-family: var(--font); background: var(--bg); color: var(--text); line-height: 1.7; font-size: 15px; }

a { color: inherit; text-decoration: none; }

/* ---- Layout ---- */
.container { max-width: 1080px; margin: 0 auto; padding: 0 20px; }

/* ---- Site Header ---- */
.site-header {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 14px 0;
  position: sticky; top: 0; z-index: 100;
}
.site-header .inner {
  display: flex; align-items: center; gap: 16px;
  max-width: 1080px; margin: 0 auto; padding: 0 20px;
}
.site-logo { font-size: 18px; font-weight: 700; white-space: nowrap; }
.site-logo a:hover { opacity: .75; }
.site-search {
  flex: 1; max-width: 480px; margin-left: auto;
  position: relative;
}
.site-search input {
  width: 100%; padding: 8px 12px 8px 36px;
  border: 1px solid var(--border); border-radius: 8px;
  font-size: 14px; background: var(--bg);
  outline: none;
}
.site-search input:focus { border-color: #94a3b8; background: #fff; }
.site-search .ico {
  position: absolute; left: 11px; top: 50%; transform: translateY(-50%);
  color: var(--muted); pointer-events: none; font-size: 14px;
}

/* ---- Hero (top page) ---- */
.hero { padding: 48px 0 32px; text-align: center; }
.hero h1 { font-size: 2em; font-weight: 800; margin-bottom: 8px; }
.hero p  { color: var(--muted); font-size: 15px; }
.stats-bar {
  display: flex; gap: 32px; justify-content: center; flex-wrap: wrap;
  margin-top: 20px;
}
.stats-bar .stat { text-align: center; }
.stats-bar .stat strong { display: block; font-size: 1.6em; font-weight: 700; }
.stats-bar .stat span { font-size: 12px; color: var(--muted); }

/* ---- Section ---- */
.section { padding: 32px 0; }
.section-header {
  display: flex; align-items: center; gap: 10px;
  margin-bottom: 20px; padding-bottom: 12px;
  border-bottom: 2px solid var(--border);
}
.section-header h2 { font-size: 1.15em; font-weight: 700; }
.section-badge {
  font-size: 11px; font-weight: 600; padding: 3px 10px;
  border-radius: 99px; white-space: nowrap;
}

/* ---- Blog Cards (top page) ---- */
.blog-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}
.blog-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 20px;
  box-shadow: var(--shadow);
  transition: box-shadow .15s, transform .15s;
  display: flex; flex-direction: column; gap: 8px;
}
.blog-card:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); }
.blog-card .card-emoji { font-size: 24px; }
.blog-card .card-name { font-size: 15px; font-weight: 700; }
.blog-card .card-desc { font-size: 13px; color: var(--muted); flex: 1; }
.blog-card .card-meta {
  display: flex; align-items: center; justify-content: space-between;
  font-size: 12px; color: var(--muted); margin-top: 4px;
}
.blog-card .card-count {
  font-weight: 600; font-size: 13px;
}
.blog-card .card-accent {
  height: 3px; border-radius: 99px; margin-bottom: 4px;
}

/* ---- Breadcrumb ---- */
.breadcrumb {
  font-size: 13px; color: var(--muted);
  padding: 16px 0 0;
  display: flex; align-items: center; gap: 6px; flex-wrap: wrap;
}
.breadcrumb a:hover { text-decoration: underline; }
.breadcrumb .sep { color: #cbd5e1; }

/* ---- Blog Index Page ---- */
.blog-hero {
  padding: 28px 0 20px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 24px;
}
.blog-hero-inner {
  display: flex; align-items: flex-start; gap: 16px;
}
.blog-hero-emoji { font-size: 36px; line-height: 1; }
.blog-hero h1 { font-size: 1.5em; font-weight: 800; }
.blog-hero p  { color: var(--muted); font-size: 14px; margin-top: 4px; }
.blog-hero-meta { font-size: 12px; color: var(--muted); margin-top: 6px; }

/* ---- Category Filter ---- */
.filter-bar {
  display: flex; gap: 8px; flex-wrap: wrap;
  margin-bottom: 20px; align-items: center;
}
.filter-btn {
  padding: 5px 14px; border-radius: 99px;
  border: 1px solid var(--border); background: var(--surface);
  font-size: 13px; cursor: pointer;
  transition: background .1s, border-color .1s;
}
.filter-btn:hover { background: #f1f5f9; }
.filter-btn.active { background: var(--accent); color: #fff; border-color: var(--accent); }
.filter-label { font-size: 13px; color: var(--muted); }

/* ---- Article Cards (blog index) ---- */
.article-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 14px;
}
.article-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 16px;
  box-shadow: var(--shadow);
  transition: box-shadow .15s, transform .15s;
  display: flex; flex-direction: column; gap: 6px;
}
.article-card:hover { box-shadow: var(--shadow-md); transform: translateY(-1px); }
.article-card .ac-title {
  font-size: 14px; font-weight: 600; line-height: 1.4;
  color: var(--text);
}
.article-card:hover .ac-title { color: var(--accent); }
.article-card .ac-meta {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  margin-top: auto; padding-top: 8px;
}
.tag {
  font-size: 11px; padding: 2px 8px; border-radius: 99px;
  background: #f1f5f9; color: var(--muted);
  white-space: nowrap;
}
.ac-date { font-size: 11px; color: var(--muted); margin-left: auto; white-space: nowrap; }

/* ---- Article Page ---- */
.article-wrap { padding: 20px 0 60px; }
.article-head { margin-bottom: 24px; }
.article-head h1 { font-size: 1.6em; font-weight: 800; line-height: 1.4; margin-top: 8px; }
.article-head .meta { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin-top: 10px; }
.article-head .date { font-size: 13px; color: var(--muted); }

.article-body {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 28px 32px;
  box-shadow: var(--shadow);
}
.article-body h4,
.article-body h5 { color: var(--accent); margin: 1.2em 0 .5em; }
.article-body p  { margin: .7em 0; }
.article-body a  { color: var(--accent); }
.article-body a:hover { text-decoration: underline; }
.article-body img { max-width: 100%; height: auto; border-radius: 6px; }
.article-body pre {
  background: #f8fafc; border: 1px solid var(--border);
  border-radius: 6px; padding: 14px 16px;
  overflow-x: auto; font-size: 13px; line-height: 1.6;
}
.article-body code {
  background: #f1f5f9; padding: 1px 5px; border-radius: 4px;
  font-size: .88em;
}
.article-body pre code { background: none; padding: 0; }
.article-body iframe { max-width: 100%; }
.article-body ul, .article-body ol { padding-left: 1.5em; margin: .7em 0; }
.article-body blockquote {
  border-left: 3px solid var(--border); margin: 1em 0;
  padding: .5em 1em; color: var(--muted);
}
.article-body table { border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 14px; }
.article-body th, .article-body td { border: 1px solid var(--border); padding: 8px 12px; }
.article-body th { background: #f8fafc; font-weight: 600; }

/* ---- Article Nav ---- */
.article-nav {
  display: flex; gap: 12px; margin-top: 28px;
  flex-wrap: wrap;
}
.article-nav a {
  flex: 1; min-width: 200px;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 14px 18px;
  box-shadow: var(--shadow);
  transition: box-shadow .15s;
  font-size: 13px;
}
.article-nav a:hover { box-shadow: var(--shadow-md); }
.article-nav .nav-label { font-size: 11px; color: var(--muted); display: block; margin-bottom: 4px; }
.article-nav .nav-title { font-weight: 600; color: var(--text); }
.article-nav .nav-next { text-align: right; }

/* ---- Empty state ---- */
.empty { text-align: center; padding: 60px 0; color: var(--muted); }

/* ---- Footer ---- */
.site-footer {
  border-top: 1px solid var(--border); padding: 24px 0;
  text-align: center; font-size: 13px; color: var(--muted);
  margin-top: 40px;
}

/* ---- Search results page ---- */
.search-results { padding: 24px 0; }
.search-results h2 { font-size: 1.1em; margin-bottom: 16px; }
.result-item {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 14px 18px;
  margin-bottom: 10px; box-shadow: var(--shadow);
  transition: box-shadow .15s;
}
.result-item:hover { box-shadow: var(--shadow-md); }
.result-item .ri-title { font-weight: 600; font-size: 15px; color: var(--text); }
.result-item:hover .ri-title { color: var(--accent, #2563eb); }
.result-item .ri-meta { font-size: 12px; color: var(--muted); margin-top: 4px; }

/* ---- Responsive ---- */
@media (max-width: 640px) {
  .blog-grid { grid-template-columns: 1fr; }
  .article-grid { grid-template-columns: 1fr; }
  .article-body { padding: 18px 16px; }
  .site-search { display: none; }
  .article-nav a { min-width: 100%; }
}
"""

# ============================================================
# JAVASCRIPT (filter + search)
# ============================================================

FILTER_JS = """
// Category filter for blog index pages
document.addEventListener('DOMContentLoaded', function() {
  const btns = document.querySelectorAll('.filter-btn');
  const cards = document.querySelectorAll('.article-card');
  let active = 'all';

  btns.forEach(btn => {
    btn.addEventListener('click', function() {
      active = this.dataset.cat;
      btns.forEach(b => b.classList.remove('active'));
      this.classList.add('active');

      let visible = 0;
      cards.forEach(card => {
        const cats = card.dataset.cats ? card.dataset.cats.split(',') : [];
        const show = active === 'all' || cats.includes(active);
        card.style.display = show ? '' : 'none';
        if (show) visible++;
      });

      const counter = document.getElementById('article-count');
      if (counter) counter.textContent = visible;
    });
  });
});
"""

SEARCH_JS = """
let searchIndex = null;

async function loadIndex() {
  if (searchIndex) return;
  try {
    const res = await fetch('../search-index.json');
    searchIndex = await res.json();
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
"""

# ============================================================
# PAGE BUILDERS
# ============================================================

def page_shell(title, content, depth=0, accent='#2563eb', extra_head='', extra_js=''):
    """depth: 0=root, 1=blog dir"""
    css_path  = '../style.css'  if depth > 0 else 'style.css'
    js_path   = '../search.js'  if depth > 0 else 'search.js'
    home_path = '../index.html' if depth > 0 else 'index.html'
    search_path = '../search.html' if depth > 0 else 'search.html'
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} - {SITE_NAME}</title>
<link rel="stylesheet" href="{css_path}">
<style>:root {{ --accent: {accent}; }}</style>
{extra_head}
</head>
<body>
<header class="site-header">
  <div class="inner">
    <div class="site-logo"><a href="{home_path}">{SITE_NAME}</a></div>
    <div class="site-search">
      <span class="ico">🔍</span>
      <input type="text" placeholder="記事を検索...">
    </div>
  </div>
</header>
{content}
<footer class="site-footer">
  <div class="container">
    {SITE_NAME} &nbsp;·&nbsp; 全8ブログ 579記事
  </div>
</footer>
<script src="{js_path}"></script>
{extra_js}
</body>
</html>"""


def build_top_page(all_blogs_data):
    total_articles = sum(len(d['articles']) for d in all_blogs_data)
    dates = []
    for d in all_blogs_data:
        for a in d['articles']:
            if a.get('date'):
                dates.append(a['date'][:7])

    # Stats
    start = min(dates) if dates else ''
    end   = max(dates) if dates else ''

    # Group cards HTML
    group_sections = ''
    for gkey in ('coding', 'design', 'review'):
        g = GROUPS[gkey]
        blogs_in_group = [b for b in all_blogs_data if b['config']['group'] == gkey]
        if not blogs_in_group: continue

        cards = ''
        for b in blogs_in_group:
            cfg = b['config']
            arts = b['articles']
            cats = set()
            for a in arts:
                for c in get_cats(a):
                    cats.add(c)
            top_cats = sorted(cats)[:5]
            tags_html = ''.join(f'<span class="tag">{c}</span>' for c in top_cats)
            dates_b = [a['date'] for a in arts if a.get('date')]
            date_range = f"{min(dates_b)[:7]} ~ {max(dates_b)[:7]}" if dates_b else ''
            cards += f"""
<a href="{cfg['slug']}/index.html" class="blog-card">
  <div class="card-accent" style="background:{g['color']}"></div>
  <div class="card-emoji">{cfg['emoji']}</div>
  <div class="card-name">{cfg['name']}</div>
  <div class="card-desc">{cfg['desc']}</div>
  <div style="display:flex;gap:4px;flex-wrap:wrap;margin-top:4px">{tags_html}</div>
  <div class="card-meta">
    <span class="card-count" style="color:{g['color']}">{len(arts)}記事</span>
    <span>{date_range}</span>
  </div>
</a>"""

        group_sections += f"""
<section class="section">
  <div class="section-header">
    <h2>{g['name']}</h2>
    <span class="section-badge" style="background:{g['light']};color:{g['color']};border:1px solid {g['border']}">{len(blogs_in_group)} ブログ</span>
  </div>
  <div class="blog-grid">{cards}</div>
</section>"""

    content = f"""
<div class="container">
  <div class="hero">
    <h1>{SITE_NAME}</h1>
    <p>Web制作・デザインの学習記録 ―― 8ブログ {total_articles}記事</p>
    <div class="stats-bar">
      <div class="stat"><strong>{total_articles}</strong><span>総記事数</span></div>
      <div class="stat"><strong>8</strong><span>ブログ</span></div>
      <div class="stat"><strong>{start[:7] if start else ''}</strong><span>学習開始</span></div>
      <div class="stat"><strong>{end[:7] if end else ''}</strong><span>最終更新</span></div>
    </div>
  </div>
  {group_sections}
</div>"""

    return page_shell(SITE_NAME, content, depth=0, accent='#2563eb')


def build_search_page():
    content = """
<div class="container search-results">
  <div class="breadcrumb">
    <a href="index.html">🏠 ホーム</a>
    <span class="sep">›</span>
    <span>検索</span>
  </div>
  <h2>記事を検索 &nbsp;<small id="result-count" style="font-size:13px;color:#64748b;font-weight:400"></small></h2>
  <div style="margin: 16px 0 24px">
    <input id="search-input" type="text" placeholder="キーワードを入力..."
      style="width:100%;max-width:560px;padding:10px 16px;border:1px solid #e2e8f0;border-radius:8px;font-size:15px;outline:none">
  </div>
  <div id="search-results"></div>
</div>"""
    return page_shell('検索', content, depth=0, accent='#2563eb')


def build_blog_index(blog_cfg, articles, group):
    slug    = blog_cfg['slug']
    accent  = group['color']
    cats    = defaultdict(int)
    for a in articles:
        for c in get_cats(a):
            cats[c] += 1
    sorted_cats = sorted(cats.keys(), key=lambda c: -cats[c])

    filter_btns = '<button class="filter-btn active" data-cat="all" style="--accent:' + accent + '">すべて</button>\n'
    for c in sorted_cats:
        filter_btns += f'<button class="filter-btn" data-cat="{c}" style="--accent:{accent}">{c} <small>({cats[c]})</small></button>\n'

    cards = ''
    for a in sorted(articles, key=lambda x: x.get('date',''), reverse=True):
        fname    = safe_filename(a['title'])
        art_cats = get_cats(a)
        data_cats = ','.join(art_cats)
        tags_html = ''.join(f'<span class="tag">{c}</span>' for c in art_cats[:3])
        cards += f"""
<a href="{fname}" class="article-card" data-cats="{data_cats}">
  <div class="ac-title">{a['title']}</div>
  <div class="ac-meta">
    {tags_html}
    <span class="ac-date">{fmt_date(a.get('date',''))}</span>
  </div>
</a>"""

    dates = [a['date'] for a in articles if a.get('date')]
    date_range = f"{min(dates)[:7]} ~ {max(dates)[:7]}" if dates else ''

    content = f"""
<div class="container">
  <div class="breadcrumb">
    <a href="../index.html">🏠 ホーム</a>
    <span class="sep">›</span>
    <span>{blog_cfg['name']}</span>
  </div>
  <div class="blog-hero">
    <div class="blog-hero-inner">
      <div class="blog-hero-emoji">{blog_cfg['emoji']}</div>
      <div>
        <h1>{blog_cfg['name']}</h1>
        <p>{blog_cfg['desc']}</p>
        <div class="blog-hero-meta">
          <span id="article-count">{len(articles)}</span>記事 &nbsp;·&nbsp; {date_range}
        </div>
      </div>
    </div>
  </div>
  <div class="filter-bar">
    <span class="filter-label">カテゴリ:</span>
    {filter_btns}
  </div>
  <div class="article-grid">{cards}</div>
</div>"""

    extra_js = f'<script>\n{FILTER_JS}\n</script>'
    return page_shell(blog_cfg['name'], content, depth=1, accent=accent, extra_js=extra_js)


def build_article(article, blog_cfg, group, prev_art=None, next_art=None):
    accent = group['color']
    art_cats = get_cats(article)
    tags_html = ''.join(f'<span class="tag" style="background:{group["light"]};color:{accent}">{c}</span>' for c in art_cats)

    nav_html = ''
    nav_parts = []
    if prev_art:
        nav_parts.append(f'<a href="{safe_filename(prev_art["title"])}" class="nav-prev"><span class="nav-label">← 前の記事</span><span class="nav-title">{prev_art["title"]}</span></a>')
    if next_art:
        nav_parts.append(f'<a href="{safe_filename(next_art["title"])}" class="nav-next" style="text-align:right"><span class="nav-label">次の記事 →</span><span class="nav-title">{next_art["title"]}</span></a>')
    if nav_parts:
        nav_html = f'<nav class="article-nav">{"".join(nav_parts)}</nav>'

    content = f"""
<div class="container article-wrap">
  <div class="breadcrumb">
    <a href="../index.html">🏠 ホーム</a>
    <span class="sep">›</span>
    <a href="index.html">{blog_cfg['name']}</a>
    <span class="sep">›</span>
    <span>{article['title']}</span>
  </div>
  <div class="article-head">
    <h1>{article['title']}</h1>
    <div class="meta">
      {tags_html}
      <span class="date">{fmt_date(article.get('date',''))}</span>
    </div>
  </div>
  <div class="article-body">
    {patch_images(article.get('content_html', ''))}
  </div>
  {nav_html}
</div>"""

    return page_shell(article['title'], content, depth=1, accent=accent)


# ============================================================
# MAIN
# ============================================================

def main():
    # Clean output dir (images/ と image-map.json は保持)
    if os.path.exists(OUT_DIR):
        for item in os.listdir(OUT_DIR):
            if item in ('images', 'image-map.json'):
                continue
            p = os.path.join(OUT_DIR, item)
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f'出力先: {OUT_DIR}')

    # Write shared CSS + JS
    with open(os.path.join(OUT_DIR, 'style.css'), 'w', encoding='utf-8') as f:
        f.write(SHARED_CSS)
    with open(os.path.join(OUT_DIR, 'search.js'), 'w', encoding='utf-8') as f:
        f.write(SEARCH_JS)
    print('style.css, search.js 書き込み完了')

    # Load all blog data
    all_blogs_data = []
    search_index   = []

    for cfg in sorted(BLOGS, key=lambda b: b['order']):
        path = os.path.join(JSON_DIR, cfg['file'])
        with open(path, encoding='utf-8') as f:
            articles = json.load(f)
        all_blogs_data.append({'config': cfg, 'articles': articles})
        print(f'  Loaded {cfg["slug"]}: {len(articles)}件')

        # Search index entries
        for a in articles:
            fname = safe_filename(a['title'])
            search_index.append({
                'title': a['title'],
                'url':   f'{cfg["slug"]}/{fname}',
                'blog':  cfg['name'],
                'date':  a.get('date', '')[:10],
                'cats':  ', '.join(get_cats(a)),
            })

    # Write search index
    with open(os.path.join(OUT_DIR, 'search-index.json'), 'w', encoding='utf-8') as f:
        json.dump(search_index, f, ensure_ascii=False)
    print(f'search-index.json: {len(search_index)}件')

    # Top page
    with open(os.path.join(OUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(build_top_page(all_blogs_data))
    print('index.html 生成')

    # Search page
    with open(os.path.join(OUT_DIR, 'search.html'), 'w', encoding='utf-8') as f:
        f.write(build_search_page())
    print('search.html 生成')

    # Blog pages + article pages
    total_articles = 0
    for bd in all_blogs_data:
        cfg      = bd['config']
        articles = bd['articles']
        group    = GROUPS[cfg['group']]
        slug_dir = os.path.join(OUT_DIR, cfg['slug'])
        os.makedirs(slug_dir, exist_ok=True)

        # Sort articles by date asc for prev/next nav
        sorted_arts = sorted(articles, key=lambda x: x.get('date', ''))

        # Blog index
        with open(os.path.join(slug_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(build_blog_index(cfg, articles, group))

        # Article pages
        for i, article in enumerate(sorted_arts):
            prev_art = sorted_arts[i - 1] if i > 0 else None
            next_art = sorted_arts[i + 1] if i < len(sorted_arts) - 1 else None
            fname    = safe_filename(article['title'])
            fpath    = os.path.join(slug_dir, fname)
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(build_article(article, cfg, group, prev_art, next_art))
            total_articles += 1

        print(f'  {cfg["slug"]}/: index + {len(articles)}記事')

    print(f'\n完了: 合計 {total_articles} 記事ページ生成')

    # Verify no broken links in index
    import re
    with open(os.path.join(OUT_DIR, 'index.html'), encoding='utf-8') as f:
        html = f.read()
    hrefs = re.findall(r'href="([^"]+)"', html)
    broken = []
    for href in hrefs:
        if href.startswith('http') or href.startswith('#'):
            continue
        full = os.path.join(OUT_DIR, href.replace('/', os.sep))
        if not os.path.exists(full):
            broken.append(href)
    if broken:
        print(f'BROKEN LINKS in index.html: {broken}')
    else:
        print('index.html リンク検証: 全OK')

main()
