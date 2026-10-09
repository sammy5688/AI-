// 逐格輸出：用無頭瀏覽器播放動畫網頁，每 1/30 秒截一張圖，交給 ffmpeg 合成影片
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const { execFileSync, spawn } = require('child_process');
const fs = require('fs');
const [,, page_path, out, fpsArg, onlyTimes] = process.argv;
const FPS = +fpsArg || 30, DUR = 52;
const UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36';
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  // 字型經由 curl 下載（走環境的代理與憑證），確保畫面用的就是預覽中的思源宋體
  await p.route(/fonts\.(googleapis|gstatic)\.com/, async route => {
    const url = route.request().url();
    const body = execFileSync('curl', ['-sS', '--fail', '-A', UA, url], { maxBuffer: 64 << 20 });
    await route.fulfill({ body, headers: { 'content-type': url.includes('googleapis') ? 'text/css' : 'font/woff2', 'access-control-allow-origin': '*' } });
  });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + page_path);
  if (onlyTimes) { fs.writeFileSync(onlyTimes, JSON.stringify(await p.evaluate(() => window.__lampTimes))); await b.close(); return; }
  await p.evaluate(() => {
    document.body.style.padding = '0';
    const w = document.querySelector('.wrap');
    [...w.children].forEach(c => { if (c.id !== 'frame') c.style.display = 'none'; });
    w.style.maxWidth = 'none'; w.style.gap = '0';
    const f = document.getElementById('frame');
    Object.assign(f.style, { width: '1080px', height: '1920px', borderRadius: '0', boxShadow: 'none' });
    document.getElementById('stage').style.transform = 'none';
  });
  for (const t of [3, 8, 13, 25, 29, 36, 39, 46, 49]) await p.evaluate(t => renderAt(t), t);   // 先讓所有字都出現一次，觸發字型下載
  await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(1500);
  const ff = spawn('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p', '-r', String(FPS), out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const N = Math.round(DUR * FPS), t0 = Date.now();
  for (let i = 0; i < N; i++) {
    await p.evaluate(t => renderAt(t), Math.min(i / FPS, DUR - .001));
    const buf = await p.screenshot({ type: 'jpeg', quality: 94, clip: { x: 0, y: 0, width: 1080, height: 1920 } });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 150 === 0) console.log(`frame ${i}/${N}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
  console.log('done', out, 'errors:', errs);
  await b.close();
})();
