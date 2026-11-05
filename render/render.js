// Render frame demi frame (deterministik) dari <folder_video>/timeline.json memakai render/mesin.html.
// Pakai: node render/render.js <folder_video> <folder_frame> [fps] [t1,t2,...]   (daftar t = hanya frame cek, PNG)
const http = require('http'), fs = require('fs'), path = require('path'); const { chromium } = require('playwright');
const ROOT = path.resolve(__dirname, '..'), EP = path.resolve(process.argv[2]), OUT = path.resolve(process.argv[3]), FPS = +(process.argv[4] || 30);
const CEK = process.argv[5] ? process.argv[5].split(',').map(Number) : null;
const MIME = {'.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.svg': 'image/svg+xml', '.woff2': 'font/woff2', '.png': 'image/png'};
const srv = http.createServer((q, s) => {
  const u = decodeURIComponent(q.url.split('?')[0]);
  const f = u.startsWith('/ep/') ? path.join(EP, u.slice(4)) : path.join(ROOT, u);
  fs.readFile(f, (e, d) => { if (e) { s.writeHead(404); s.end(); return; } s.writeHead(200, {'Content-Type': MIME[path.extname(f)] || 'application/octet-stream'}); s.end(d); });
});
srv.listen(0, '127.0.0.1', async () => {
  fs.mkdirSync(OUT, {recursive: true});
  const b = await chromium.launch(); const p = await b.newPage({viewport: {width: 720, height: 1280}});
  let galat = 0; p.on('pageerror', e => { galat++; console.error('GALAT HALAMAN', e.message); });
  await p.goto(`http://127.0.0.1:${srv.address().port}/render/mesin.html?tl=/ep/timeline.json`);
  await p.waitForFunction(() => window.READY === true, null, {timeout: 120000});
  const tl = JSON.parse(fs.readFileSync(path.join(EP, 'timeline.json'))); const t0 = Date.now();
  const daftar = CEK || Array.from({length: Math.round(tl.durasi * FPS)}, (_, i) => i / FPS);
  for (const [i, t] of daftar.entries()) {
    await p.evaluate(t => window.render(t), t);
    await p.screenshot(CEK ? {path: path.join(OUT, `cek_${String(i).padStart(2, '0')}.png`)} : {path: path.join(OUT, `f${String(i).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 92});
  }
  const kosakata = await p.evaluate(() => window.KOSAKATA);
  fs.writeFileSync(path.join(OUT, 'kosakata-mesin.json'), JSON.stringify(kosakata));
  console.log(JSON.stringify({frame: daftar.length, detik: +((Date.now() - t0) / 1000).toFixed(1), galat}));
  await b.close(); srv.close(); process.exit(galat ? 1 : 0);
});
