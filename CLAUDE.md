# CLAUDE.md — 学習ポータル プロジェクト

## プロジェクト一言サマリ
はてなブログ8本をスクレイピングして静的HTMLサイト(docs/)に変換するアーカイブ。
デプロイ先: GitHub Pages（docs/ フォルダを公開）。

## ディレクトリ（重要なものだけ）
```
web-hakubyo/
├── JSON/                  # スクレイピング済みJSON（触らない）
├── docs/                  # デプロイ対象の静的HTML（ここを編集・確認）
│   ├── index.html         # トップ（ブログ一覧）
│   ├── style.css          # 共通CSS
│   ├── search.js/html     # 検索機能
│   ├── images/            # 画像（Git管理・約218MB）
│   └── {slug}/            # 各ブログのHTML群
├── generate_site.py       # JSON → docs/ を生成するスクリプト
├── download_images.py     # 画像DLスクリプト
├── hatena_scraper.js      # Chrome Console で使うスクレイパー
├── image-map.json         # URL→ローカルファイル名マッピング
└── _archive/              # 不要な旧ファイル置き場（触らない）
```

## ブログスラッグ一覧
web-hakubyo / html-css-exercises / javascript / js-exercises /
illustrator / photoshop / ps-ai-practice / review / sass（手動）

## よくあるタスクと注意点

### docs/ を直接編集するとき
- generate_site.py を再実行すると **上書きされる**
- sass/ は手動作成のため再実行しても消えない（BLOGS リスト外）
- 再実行後は index.html の sass セクションが消えるので注意

### generate_site.py を実行するとき
```bash
python generate_site.py
```
パスは `__file__` 基準で解決済み（ハードコード不要）。

### 記事を新規追加するとき
1. `hatena_scraper.js` を Chrome Console で実行 → JSON を `JSON/` に配置
2. `python download_images.py`（画像取得）
3. `python generate_site.py`（サイト再生成）
4. git push → GitHub Pages に自動反映

## トークン節約ルール（Claude への指示）
- ファイル全体を読まず必要な行範囲だけ Read する
- generate_site.py は 700 行超。**変更前に該当箇所を grep してから最小限 Edit**
- JSON/ の中身は読まない（大容量）
- docs/images/ の中身は読まない（3000ファイル超）
- 不明点はまず SPEC.md を参照してから調査

## デプロイ構成
- **GitHub Pages**（無料、静的ホスティング）
- リポジトリの `docs/` フォルダを Pages の公開ソースに設定
- push するだけで自動反映（CI不要）
- 画像は Git に含める（各ファイル100MB以下、合計218MBはPages制限内）

## 既知の注意点
- `docs/sass/` は index.html に手動でリンクを追加している（自動生成外）
- index.html の「9ブログ 588記事」は generate_site.py が生成する数字と手動追記の sass を合算した値
