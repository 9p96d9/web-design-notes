#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
画像ダウンローダー
JSONのcontent_htmlから画像URLを収集 → site/images/ にダウンロード
URL→ローカルパス マッピングを image-map.json に保存
"""

import json, os, re, sys, io, time
import urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from pathlib import Path
import hashlib

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ============================================================
_BASE     = os.path.dirname(os.path.abspath(__file__))
JSON_DIR  = os.path.join(_BASE, 'JSON')
OUT_DIR   = os.path.join(_BASE, 'site')
IMG_DIR   = os.path.join(OUT_DIR, 'images')
MAP_FILE  = os.path.join(_BASE, 'image-map.json')
MAX_WORKERS = 8
TIMEOUT     = 20
HEADERS     = {'User-Agent': 'Mozilla/5.0 (compatible; site-archiver/1.0)'}
# ============================================================

def url_to_filename(url):
    """URLからローカルファイル名を生成"""
    # cdn-ak.f.st-hatena.com/images/fotolife/x/username/YYYYMMDD/YYYYMMDDHHMMSS.jpg
    m = re.search(r'fotolife/(.+)$', url)
    if m:
        # x/username/YYYYMMDD/YYYYMMDDHHMMSS.jpg → x_username_YYYYMMDDHHMMSS.jpg
        parts = m.group(1).split('/')
        # 最後のファイル名だけ使う（タイムスタンプなので衝突しにくい）
        fname = parts[-1]
        # 念のため同名衝突対策：ユーザー名をプレフィックスに
        if len(parts) >= 2:
            fname = f'{parts[1]}_{fname}'
        return fname
    # それ以外は URL のハッシュ + 拡張子
    ext = os.path.splitext(url.split('?')[0])[-1] or '.jpg'
    return hashlib.md5(url.encode()).hexdigest()[:12] + ext

def collect_image_urls(json_dir):
    """全JSONから画像URLを収集"""
    url_to_blogs = defaultdict(set)
    files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
    for fname in files:
        with open(os.path.join(json_dir, fname), encoding='utf-8') as f:
            data = json.load(f)
        for item in data:
            html = item.get('content_html', '')
            urls = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html)
            for url in urls:
                if url.startswith('data:') or not url.startswith('http'):
                    continue
                url_to_blogs[url].add(fname)
    return url_to_blogs

def download_one(url, img_dir):
    """1枚ダウンロード。成功: (url, localpath), 失敗: (url, None)"""
    fname    = url_to_filename(url)
    out_path = os.path.join(img_dir, fname)

    if os.path.exists(out_path):
        return url, fname, 'skip'

    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = resp.read()
        with open(out_path, 'wb') as f:
            f.write(data)
        return url, fname, 'ok'
    except Exception as e:
        return url, None, f'error: {e}'

def main():
    os.makedirs(IMG_DIR, exist_ok=True)

    # 既存マップ読み込み（再実行時スキップ用）
    existing_map = {}
    if os.path.exists(MAP_FILE):
        with open(MAP_FILE, encoding='utf-8') as f:
            existing_map = json.load(f)

    print('画像URL収集中...')
    url_to_blogs = collect_image_urls(JSON_DIR)
    all_urls = list(url_to_blogs.keys())
    print(f'収集: {len(all_urls)}件\n')

    image_map = dict(existing_map)
    ok = skip = err = 0
    errors = []

    print(f'ダウンロード開始 (並列{MAX_WORKERS})')
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(download_one, url, IMG_DIR): url for url in all_urls}
        done = 0
        for future in as_completed(futures):
            url, fname, status = future.result()
            done += 1
            if status == 'ok':
                image_map[url] = fname
                ok += 1
            elif status == 'skip':
                image_map[url] = fname
                skip += 1
            else:
                err += 1
                errors.append((url, status))

            if done % 100 == 0 or done == len(all_urls):
                print(f'  [{done}/{len(all_urls)}] OK:{ok} SKIP:{skip} ERR:{err}')

    # マップ保存
    with open(MAP_FILE, 'w', encoding='utf-8') as f:
        json.dump(image_map, f, ensure_ascii=False, indent=2)

    print(f'\n完了: OK={ok}  SKIP={skip}  ERROR={err}')
    print(f'image-map.json: {len(image_map)}件')

    if errors:
        print(f'\nエラー一覧 (最初の10件):')
        for url, msg in errors[:10]:
            print(f'  {msg}')
            print(f'  {url[:80]}')

    # ダウンロード済みファイルサイズ確認
    total_size = sum(os.path.getsize(os.path.join(IMG_DIR, f))
                     for f in os.listdir(IMG_DIR)
                     if os.path.isfile(os.path.join(IMG_DIR, f)))
    print(f'\nimages/ 合計: {len(os.listdir(IMG_DIR))}ファイル, {total_size/1024/1024:.1f} MB')

main()
