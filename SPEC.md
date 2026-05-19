# 学習ポータル 仕様書

## プロジェクト概要

はてなブログ複数（8ブログ、588記事）をスクレイピングし、  
1つの静的HTMLサイトに統合する学習アーカイブポータル。

- **サイト名**: 学習ポータル
- **コンテンツ**: Web制作・デザイン（HTML/CSS, JavaScript, Illustrator, Photoshop）
- **技術スタック**: Python（サイト生成）+ Vanilla JS + 静的HTML

---

## ディレクトリ構成

```
web-hakubyo/
├── hatena_scraper.js      # Step1: ブラウザConsoleで実行 → 記事JSONをDL
├── download_images.py     # Step2: JSON内の画像をローカルにDL
├── generate_site.py       # Step3: JSONからHTMLサイトを生成
├── image-map.json         # 画像URL → ローカルファイル名マッピング
│
├── JSON/                  # スクレイピング済みJSON（8ブログ分）
│   ├── blog_articles.json                          # Web白描
│   ├── HTML_CSS__演習プロンプト__articles.json
│   ├── JavaScript_articles.json
│   ├── JavaScript_演習プロンプト__articles.json
│   ├── Illustrator_基礎_articles.json
│   ├── Photoshop_基礎_articles.json
│   ├── Photoshop___Illusrator_実践演習_articles.json
│   └── The_復習_articles.json
│
└── docs/                  # 生成された静的サイト（デプロイ対象）
    ├── index.html          # トップページ（ブログ一覧）
    ├── style.css           # 共通スタイル
    ├── search.html         # 全文検索ページ
    ├── search.js           # 検索ロジック（クライアントサイド）
    ├── search-index.json   # 検索インデックス（タイトル・カテゴリ）
    ├── images/             # ダウンロード済み画像（3082ファイル / 約218MB）
    ├── web-hakubyo/        # ブログ: Web白描（60記事）
    ├── html-css-exercises/ # ブログ: HTML/CSS演習プロンプト
    ├── javascript/         # ブログ: JavaScript
    ├── js-exercises/       # ブログ: JavaScript演習プロンプト
    ├── illustrator/        # ブログ: Illustrator基礎
    ├── photoshop/          # ブログ: Photoshop基礎
    ├── ps-ai-practice/     # ブログ: Ps・Ai実践演習
    ├── review/             # ブログ: The復習
    ├── sass/               # Sass解説ページ（手動作成、生成対象外）
    └── Illustrator_ex/     # Illustrator練習用.aiファイル素材
```

---

## ツール詳細

### hatena_scraper.js
- **役割**: はてなブログの全記事をスクレイピング
- **実行方法**: Chromeの開発者ツール(F12) → Console に貼り付けて実行
- **出力**: `{ブログ名}_articles.json`（タイトル・日付・カテゴリ・本文HTML）
- **制限**: 記事間に3秒のウェイト（サーバー負荷軽減）
- **汎用**: どのはてなブログでも使用可能

### download_images.py
- **役割**: JSONのcontent_html内の画像URLをダウンロード
- **出力先**: `docs/images/`
- **マッピング**: URL → ローカルファイル名を `image-map.json` に保存
- **並列数**: 8スレッド、タイムアウト20秒
- **再実行**: 既存ファイルはスキップ（冪等）

### generate_site.py
- **役割**: JSON + image-map.json からHTMLサイトを生成
- **生成内容**:
  - `docs/index.html`（ポータルトップ）
  - 各ブログの `index.html`（記事一覧）
  - 各記事の個別HTMLファイル
  - `search-index.json`（検索用）
- **画像処理**: `patch_images()` で外部URL → `../images/ローカルパス` に置換

---

## ブログ一覧

| slug | ブログ名 | グループ | カテゴリ |
|------|---------|---------|---------|
| web-hakubyo | Web白描 | Web コーディング | HTML/CSS/Webリテラシー基礎 |
| html-css-exercises | HTML/CSS 演習プロンプト | Web コーディング | HTML/CSS演習 |
| javascript | JavaScript | Web コーディング | JS基礎〜応用 |
| js-exercises | JavaScript 演習プロンプト | Web コーディング | JS演習 |
| illustrator | Illustrator 基礎 | デザイン | Adobe Illustrator |
| photoshop | Photoshop 基礎 | デザイン | Adobe Photoshop |
| ps-ai-practice | Photoshop/Illustrator 実践演習 | デザイン | Ps・Ai実践 |
| review | The 復習 | 総合復習 | Web制作・デザイン全般 |

---

## サイト生成フロー

```
[はてなブログ]
    ↓ hatena_scraper.js（Chromeコンソール）
[JSON/*.json]
    ↓ download_images.py
[docs/images/ + image-map.json]
    ↓ generate_site.py
[docs/ 静的HTML完成]
    ↓ GitHub Push → デプロイ
[公開URL]
```

---

## デプロイ方針

### 採用: GitHub Pages（無料）
- **理由**: 静的サイトのみ、更新頻度低い、無料枠で十分
- **公開ソース**: リポジトリの `docs/` フォルダ
- **画像**: Git に含める（各ファイル 100MB 以下、合計 218MB → Pages 1GB 制限内）
- **自動反映**: `git push` だけで更新完了（CI/CD 不要）

### セットアップ手順（初回）
```bash
# 1. GitHubでリポジトリ作成（Private or Public どちらでも可）
# 2. git init & push
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/{ユーザー名}/{リポジトリ名}.git
git push -u origin main

# 3. GitHub → Settings → Pages → Source: Deploy from branch
#    Branch: main / Folder: /docs → Save
```

### 更新時
```bash
git add docs/
git commit -m "update articles"
git push
```
→ 数十秒でサイトに反映。

---

## 注意事項・既知の問題

### sass/ ディレクトリ
`docs/sass/` は手動作成されたもの。  
`generate_site.py` の BLOGS リストに含まれていないため、サイト再生成しても上書きされないが、  
`index.html` には自動リンクされない。手動でトップページに追加が必要。

---

## 手動記事の管理

### manual-articles.json

`docs/manual-articles.json` が全ブログ横断の手動記事マニフェスト（単一の真実の源）。

```json
{
  "blog": "web-hakubyo",   // ブログスラッグ
  "blogName": "Web白描",   // 表示名（検索結果で使用）
  "file": "slug.html",
  "title": "記事タイトル",
  "category": "カテゴリ名",
  "date": "YYYY/MM/DD"
}
```

手動記事を追加するときは **このファイルにエントリを追加するだけ**。index.html は触らない。

### 自動化の仕組み

各ブログの `index.html` は `<body data-blog="{slug}">` を持ち、DOMContentLoaded 時に：
1. `../manual-articles.json` を fetch して自ブログ分を抽出
2. 記事カードを `.article-grid` 先頭に挿入
3. 記事数カウントを更新
4. 新カテゴリのフィルターボタンを自動追加

`docs/search.js` も `manual-articles.json` を読み込み、検索対象に追加している。

---

## 手動記事 HTML テンプレート

手動記事を生成するときはこの構造に従う。
**新しい CSS パターンを追加したときはここを更新する。**

### head・共通スタイル

```html
<link rel="stylesheet" href="../style.css">
<style>:root { --accent: #2563eb; }
/* ブログカラー: web-hakubyo=#2563eb / review=#0891b2 */
</style>
```

### 利用可能な CSS クラス

| クラス | 用途 |
|---|---|
| `.map-table` | 比較表（th に背景色・偶数行グレー） |
| `.code-block` | コードブロック（黒背景・monospace）|
| `.flow-box` | フロー図（青左ボーダー・monospace・行間広め）|
| `.point-box` | キーポイント（黄左ボーダー）|
| `.warn-box` | 警告・失敗パターン（赤左ボーダー）|
| `.ok-box` | 成功・推奨（緑左ボーダー）|
| `.section` | 各セクションの wrapper div |

`.code-block` 内のスパン: `.cm`（コメント・グレー）`.kw`（キーワード・水色）`.st`（文字列・緑）

### ページ骨格

```html
<header class="site-header">
  <div class="inner">
    <div class="site-logo"><a href="../index.html">学習ポータル</a></div>
    <div class="site-search"><span class="ico">🔍</span><input type="text" placeholder="記事を検索..."></div>
  </div>
</header>

<div class="container article-wrap">
  <div class="breadcrumb">
    <a href="../index.html">🏠 ホーム</a>
    <span class="sep">›</span>
    <a href="index.html">{ブログ名}</a>
    <span class="sep">›</span>
    <span>{記事タイトル}</span>
  </div>
  <div class="article-head">
    <h1>{タイトル}<br><small style="font-size:.6em;font-weight:400;color:#64748b">{サブタイトル}</small></h1>
    <div class="meta">
      <span class="tag" style="background:#eff6ff;color:#2563eb">{カテゴリ}</span>
      <span class="date">{YYYY/MM/DD}</span>
    </div>
  </div>
  <div class="article-body">
    <div class="section">
      <h4 id="{anchor}">{セクションタイトル}</h4>
      {本文}
    </div>
  </div>
</div>

<footer class="site-footer">
  <div class="inner"><p>学習ポータル</p></div>
</footer>
```

### index.html への記事カード追加

```html
<a href="{slug}.html" class="article-card" data-cats="{カテゴリ}">
  <div class="ac-title">{タイトル}</div>
  <div class="ac-meta">
    <span class="tag">{カテゴリ}</span>
    <span class="ac-date">{YYYY/MM/DD}</span>
  </div>
</a>
```

カード追加後に更新する数値:
- `<span id="article-count">N</span>` を +1
- カテゴリが新規なら filter-btn を追加: `<button class="filter-btn" data-cat="{カテゴリ}" style="--accent:#2563eb">{カテゴリ} <small>(N)</small></button>`
