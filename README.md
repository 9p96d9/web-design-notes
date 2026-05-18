# 学習ポータル

はてなブログ 9ブログ・588記事を1サイトに統合した学習アーカイブ。
HTML/CSS・JavaScript・Sass・Illustrator・Photoshopの学習記録。

**デプロイ**: GitHub Pages（`site/` フォルダを公開）

---

## 初回 GitHub Pages セットアップ

```bash
# 1. GitHubで新規リポジトリを作成（名前は任意、Public推奨）

# 2. ローカルで git 初期化 & push
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/{ユーザー名}/{リポジトリ名}.git
git branch -M main
git push -u origin main

# 3. GitHubの Settings → Pages → Source:
#    "Deploy from a branch" → Branch: main / Folder: /site → Save
```

数分後に `https://{ユーザー名}.github.io/{リポジトリ名}/` で公開される。

---

## 記事を更新するとき

### 新しいブログを追加する場合
1. Chrome で対象ブログを開き F12 → Console に `hatena_scraper.js` を貼り付けて実行
2. ダウンロードされた JSON を `JSON/` に配置
3. `python download_images.py`
4. `generate_site.py` の `BLOGS` リストに追記
5. `python generate_site.py`
6. `git add . && git commit -m "add blog" && git push`

### 既存記事の追加のみ（JSON更新 → サイト再生成）
```bash
python download_images.py   # 新しい画像があれば
python generate_site.py
git add site/ image-map.json
git commit -m "update articles"
git push
```

---

## ブログ一覧

| ブログ | スラッグ | 記事数 |
|--------|---------|-------|
| Web白描 | web-hakubyo | 59 |
| HTML/CSS 演習プロンプト | html-css-exercises | 22 |
| JavaScript | javascript | 55 |
| JavaScript 演習プロンプト | js-exercises | 28 |
| Sass入門（手動） | sass | 9 |
| Illustrator 基礎 | illustrator | 45 |
| Photoshop 基礎 | photoshop | 51 |
| Ps・Ai 実践演習 | ps-ai-practice | 221 |
| The 復習 | review | 98 |

---

## 注意

- `sass/` は `generate_site.py` の管理外（手動作成）。再生成しても消えない
- `generate_site.py` は `site/` を上書き生成する。sass 以外のカスタム編集は消える
- 詳細は `SPEC.md` 参照
