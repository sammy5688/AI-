// 每日功課：離線用的快取。修改內容後，把版本號加 1，大家下次打開就會更新。
const VERSION = 'meiri-gongke-v55';
const FILES = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png', './icon-maskable-512.png', './apple-touch-icon.png', './audio/music_loop.mp3', './audio/list.json', './audio/timing.json',
  './audio/bowl.mp3', './audio/calm_1.mp3', './audio/calm_intro.mp3', './audio/close.mp3', './audio/huixiang.mp3', './audio/mantra_chant.mp3', './audio/mantra_intro.mp3', './audio/pray_intro.mp3', './audio/thanks_1.mp3', './audio/thanks_intro.mp3', './audio/thanks_r1.mp3', './audio/thanks_r2.mp3', './audio/thanks_r3.mp3', './audio/wen_1.mp3', './audio/wen_2.mp3', './audio/wen_3.mp3', './audio/wen_intro.mp3', './audio/wen_r1.mp3', './audio/wen_r2.mp3', './audio/wen_r3.mp3', './audio/wen_r4.mp3', './audio/yuan_1.mp3', './audio/yuan_intro.mp3'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});

// 音樂與錄音：手機播放時會分段讀取，這裡從快取切出需要的那一段
async function media(req) {
  const cache = await caches.open(VERSION);
  let res = await cache.match(req.url);
  if (!res) {
    try {
      res = await fetch(req.url);
      if (res.status !== 200) return res;
      cache.put(req.url, res.clone());
    } catch (e) { return fetch(req); }
  }
  const range = req.headers.get('range');
  if (!range) return res;
  const buf = await res.arrayBuffer();
  const m = /bytes=(\d*)-(\d*)/.exec(range) || [];
  const start = m[1] ? +m[1] : 0;
  const end = m[2] ? Math.min(+m[2], buf.byteLength - 1) : buf.byteLength - 1;
  return new Response(buf.slice(start, end + 1), {
    status: 206,
    headers: {
      'Content-Type': res.headers.get('Content-Type') || 'audio/mpeg',
      'Content-Range': `bytes ${start}-${end}/${buf.byteLength}`,
      'Content-Length': String(end - start + 1),
      'Accept-Ranges': 'bytes'
    }
  });
}

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.hostname.endsWith('fonts.googleapis.com') || url.hostname.endsWith('fonts.gstatic.com')) {
    e.respondWith(caches.open(VERSION).then(async c => {
      const hit = await c.match(req);
      const net = fetch(req).then(r => { c.put(req, r.clone()); return r; }).catch(() => hit);
      return hit || net;
    }));
    return;
  }
  if (url.origin !== location.origin) return;
  if (/\.(mp3|m4a)$/i.test(url.pathname)) { e.respondWith(media(req)); return; }
  e.respondWith(fetch(req).then(r => {
    const copy = r.clone(); caches.open(VERSION).then(c => c.put(req, copy)); return r;
  }).catch(() => caches.match(req).then(hit => hit || caches.match('./index.html'))));
});
