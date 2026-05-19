# 記事管理

## 未公開（ここにブロックを追加 → 確認後に生成トリガー）

<!--
新記事を追加するときはこのテンプレートをコピーして埋める。
ユーザーが「OK」と言った時点でHTML生成・index.html更新・完了欄移動を一気に実行する。

### article: {slug（ファイル名から拡張子を除いた値）}
- blog: {web-hakubyo / javascript / review など}
- file: {slug}.html
- title: {記事タイトル}
- category: {カテゴリ名}
- date: {YYYY-MM}
- sections:
  1.
  2.
  3.
-->



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

## 手動追加記事

`generate_site.py` の対象外のため手動で作成・管理する記事の一覧。

### review（The 復習）

| ファイル名 | タイトル | カテゴリ | ステータス |
|---|---|---|---|
| `ガチャアプリ制作まとめ.html` | 授業まとめ｜ガチャアプリ制作（フォルダ整理〜画像書き出し・実装） | JavaScript | ✅ 作成済 |

### web-hakubyo（Web白描）

| ファイル名 | タイトル | カテゴリ | ステータス |
|---|---|---|---|
| `ai-native-development.html` | AIと共同開発する技術 — SPEC駆動・自走エージェントの設計思想 | AI・開発手法 | ✅ 作成済 |
| `chrome-oauth-layers.html` | 拡張機能を消してもログイン状態が残る理由 — Chrome の OAuth 階層構造 | Webリテラシー | ✅ 作成済 |

#### ガチャアプリ記事の構成

1. フォルダ構成の整理（portfolio/ ディレクトリ構造・CSSパス修正）
2. 画像素材のダウンロード（キャラ18枚・ランクアイコン3枚・ガチャ本体・SSR背景）
3. Photoshopでの画像作成（カードサイズ560×720・レイヤーグループ構成）
4. 画像の書き出し（SSR=JPEG/SR・R=PNG-24・背景透明）
5. 設計（ランク別配列・確率ロジック・for文で3枠処理）
6. HTML（構造）
7. JavaScript（コード全文＋ポイント①②③解説）
8. CSS（コード全文）
9. 次回予告

#### 手動追加の手順メモ

- `docs/review/{ファイル名}.html` を作成
- `docs/review/index.html` の article-grid 先頭にカード追加
- 記事数・カテゴリ件数・日付範囲を更新
