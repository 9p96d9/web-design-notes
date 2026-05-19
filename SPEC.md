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

### パスのハードコード（要修正）
`generate_site.py` と `download_images.py` の先頭で以下のパスが固定されている：
```python
# 現状（Desktopを参照 → 動かない）
JSON_DIR = r'c:\Users\user\Desktop\web-hakubyo\JSON'
OUT_DIR  = r'c:\Users\user\Desktop\web-hakubyo\docs'

# 実際のプロジェクトパス
JSON_DIR = r'c:\iino\web-hakubyo\JSON'
OUT_DIR  = r'c:\iino\web-hakubyo\docs'
```
→ スクリプト実行前に修正必須

### sass/ ディレクトリ
`docs/sass/` は手動作成されたもの。  
`generate_site.py` の BLOGS リストに含まれていないため、サイト再生成しても上書きされないが、  
`index.html` には自動リンクされない。手動でトップページに追加が必要。

---

## 記事案（フルスタック開発経験を活かした追加記事）

GTOポーカー分析アプリ（Chrome拡張 × Firebase × FastAPI × AWS）の開発経験をもとに書ける記事案。
対象ブログ: `web-hakubyo`（Webリテラシー）または `javascript`（JS技術系）。

### Webリテラシー系（web-hakubyo）

| タイトル案 | 概要 | 難易度 |
|---|---|---|
| JavaScriptの世界地図 ✅ | Node.js・npm・React・TypeScript・Next.jsを整理する | 初級 |
| AIが動画を編集する仕組み — FFmpegとClaude Codeの正体 ✅ | AI+CLIツール連携の構造・FFmpegとは・BOM問題などを実例で解説 | 初級 |
| Webアプリの裏側 — クライアントとサーバーの通信 | ブラウザとサーバーがどうHTTPでやりとりするか。PHPの授業と接続できる | 初級 |
| GitとGitHubを使う理由 | バージョン管理の概念・git push で公開が変わる体験 | 初級 |
| クラウドって何？ — AWSとVercelとGitHub Pagesの違い | 静的/動的サイトのホスティング選択肢を整理 | 初級〜中級 |
| CI/CDとは — GitHub Actionsで自動デプロイを作った話 | コードをpushしたら自動でサーバーが更新される仕組み | 中級 |
| AIのAPIを使ったWebアプリ開発 | Groq/Gemini APIを叩いて結果を画面に表示する構造 | 中級 |

### JavaScript技術系（javascript）

| タイトル案 | 概要 | 難易度 |
|---|---|---|
| WebSocketとは — リアルタイム通信の仕組み | HTTPとの違い、双方向通信が必要な場面（チャット・ゲーム等） | 中級 |
| Chrome拡張機能の作り方（MV3） | manifest.json・background.js・content.jsの役割分担 | 中級 |
| SSE（Server-Sent Events）— サーバーからブラウザへ通知を送る | チャットの「打ってる」表示やAI出力のストリーミングの仕組み | 中級 |
| Firebaseを使ったログイン機能の作り方 | Google認証でサインインし、Firestoreにデータを保存する基礎 | 中級 |
| Dockerでアプリを動かす — コンテナの概念 | 「環境ごと持ち運ぶ」箱の発想。npm installが要らなくなる理由 | 中級〜上級 |

### アプリ紹介・まとめ系

| タイトル案 | 概要 |
|---|---|
| ポーカーAI分析ツールを作った話 — 全体アーキテクチャ解説 | Chrome拡張でデータ収集→FastAPIで処理→Firestoreに保存→AIで分析の全フロー |
| 「PHPしか知らなかった」から「AWS+Docker+CI/CD」まで | 学校で習ったWebの知識がどう実務レベルへ発展するかのロードマップ |

---

## 授業まとめ記事（手動追加）

授業内容をそのまま記事化したもの。対象ブログ: `review`（The復習）。

| ファイル名 | タイトル | カテゴリ | ステータス |
|---|---|---|---|
| `ガチャアプリ制作まとめ.html` | 授業まとめ｜ガチャアプリ制作（フォルダ整理〜画像書き出し・実装） | JavaScript | ✅ 作成済 |

### ガチャアプリ記事の構成

1. フォルダ構成の整理（portfolio/ ディレクトリ構造・CSSパス修正）
2. 画像素材のダウンロード（キャラ18枚・ランクアイコン3枚・ガチャ本体・SSR背景）
3. Photoshopでの画像作成（カードサイズ560×720・レイヤーグループ構成）
4. 画像の書き出し（SSR=JPEG/SR・R=PNG-24・背景透明）
5. 設計（ランク別配列・確率ロジック・for文で3枠処理）
6. HTML（構造）
7. JavaScript（コード全文＋ポイント①②③解説）
8. CSS（コード全文）
9. 次回予告

### 追加手順メモ（generate_site.py 非対象のため手動）
- `docs/review/ガチャアプリ制作まとめ.html` を作成
- `docs/review/index.html` の article-grid 先頭にカード追加
- 記事数 98 → 99、JavaScript カテゴリ (3) → (4) に更新
- 日付範囲 2026-03 → 2026-05 に更新
