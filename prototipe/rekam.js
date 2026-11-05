// Merekam uji adegan ke video. Pakai: node rekam.js <A|B> <keluar.webm>
const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs');
(async () => {
  const v = process.argv[2] || 'A', out = process.argv[3] || `uji-${v}.webm`;
  const dir = fs.mkdtempSync('/tmp/rek-'); const t0 = Date.now();
  const b = await chromium.launch(); const c = await b.newContext({ viewport: { width: 720, height: 1280 }, recordVideo: { dir, size: { width: 720, height: 1280 } } });
  const p = await c.newPage(); await p.goto('file://' + path.resolve(__dirname, 'uji-adegan.html') + '?v=' + v); await p.waitForTimeout(1500);
  const offset = (Date.now() - t0) / 1000; await p.evaluate(() => window.start()); await p.waitForTimeout(16500);
  const vid = p.video(); await c.close(); fs.copyFileSync(await vid.path(), out); await b.close(); console.log('offset', offset.toFixed(2));
})();
