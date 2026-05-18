/*
============================================================
  はてなブログ 汎用スクレイピングスクリプト
  
  ★ どのはてなブログでも使えます！
  
  【手順】
  1. スクレイピングしたいブログをChromeで開く
  2. F12 → Console タブ
  3. このコード全体を貼り付けて Enter
  4. 自動でJSONファイルがダウンロードされます
============================================================
*/

(async function() {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const BASE = location.origin;
  const BLOG_NAME = document.title.split(' - ')[0] || document.title;
  
  console.log('%c=== ' + BLOG_NAME + ' スクレイピング開始 ===', 'color:green;font-size:16px');

  // Step 1: アーカイブから全記事URLを取得
  console.log('Step 1: 全記事URLを収集中...');
  let allUrls = [];
  let page = 1;
  
  while (true) {
    let archiveUrl = BASE + '/archive' + (page > 1 ? '?page=' + page : '');
    console.log('  archive page ' + page + ': ' + archiveUrl);
    
    try {
      let resp = await fetch(archiveUrl);
      if (!resp.ok) {
        console.log('  HTTP ' + resp.status + ' - 停止');
        break;
      }
      let html = await resp.text();
      let doc = new DOMParser().parseFromString(html, 'text/html');
      let links = doc.querySelectorAll('a.entry-title-link');
      
      if (links.length === 0) {
        console.log('  記事なし - 最終ページ');
        break;
      }
      
      let newCount = 0;
      links.forEach(a => {
        let href = a.href;
        if (href && href.includes('/entry/') && !allUrls.includes(href)) {
          allUrls.push(href);
          newCount++;
        }
      });
      
      console.log('  -> ' + newCount + '件追加 (累計: ' + allUrls.length + ')');
      
      if (newCount === 0) break;
      
      // 次のページがあるか確認
      let nextLink = doc.querySelector('a.pager-next') || 
                     Array.from(doc.querySelectorAll('a')).find(a => a.textContent.includes('次のページ'));
      if (!nextLink) {
        console.log('  最終ページ到達');
        break;
      }
      
      page++;
      await sleep(2000);
    } catch(e) {
      console.log('  エラー: ' + e.message);
      break;
    }
  }
  
  console.log('%c合計 ' + allUrls.length + ' 記事を発見', 'color:blue;font-size:14px');
  
  if (allUrls.length === 0) {
    console.log('%cURLが取得できませんでした', 'color:red;font-size:14px');
    return;
  }

  // Step 2: 各記事を取得
  console.log('\nStep 2: 各記事の内容を取得中...\n');
  let articles = [];
  
  for (let i = 0; i < allUrls.length; i++) {
    let url = allUrls[i];
    let short = decodeURIComponent(url.split('/entry/')[1] || '').substring(0, 50);
    
    try {
      let resp = await fetch(url);
      if (!resp.ok) {
        console.log('[' + (i+1) + '/' + allUrls.length + '] NG(' + resp.status + '): ' + short);
        await sleep(3000);
        continue;
      }
      
      let html = await resp.text();
      let doc = new DOMParser().parseFromString(html, 'text/html');
      
      let titleEl = doc.querySelector('.entry-title-link') || doc.querySelector('.entry-title');
      let title = titleEl ? titleEl.textContent.trim() : '';
      
      let dateEl = doc.querySelector('time.entry-date') || doc.querySelector('.date a');
      let date = dateEl ? dateEl.textContent.trim() : '';
      
      let cats = Array.from(doc.querySelectorAll('.entry-categories a')).map(a => a.textContent.trim());
      
      let body = doc.querySelector('.entry-content');
      let text = body ? body.innerText.trim() : '';
      let bodyHtml = body ? body.innerHTML : '';
      
      articles.push({ url, title, date, categories: cats, content_text: text, content_html: bodyHtml });
      console.log('[' + (i+1) + '/' + allUrls.length + '] OK: ' + title);
      
    } catch(e) {
      console.log('[' + (i+1) + '/' + allUrls.length + '] ERROR: ' + e.message);
    }
    
    if (i < allUrls.length - 1) await sleep(3000);
  }

  // Step 3: ダウンロード
  console.log('%c\n=== 完了！ ===', 'color:green;font-size:16px');
  console.log('成功: ' + articles.length + ' / ' + allUrls.length);

  let safeName = BLOG_NAME.replace(/[^a-zA-Z0-9\u3000-\u9FFF]/g, '_').substring(0, 30);
  let filename = safeName + '_articles.json';
  
  let blob = new Blob([JSON.stringify(articles, null, 2)], {type: 'application/json'});
  let a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  
  console.log('%c' + filename + ' をダウンロードしました！', 'color:blue;font-size:14px');
})();
