// Render an HTML file to PDF (and optional per-page PNG previews) with Chromium.
// usage: node render.mjs <input.html> <output.pdf> [--png <dir>] [--scale 1.5] [--width 297mm --height 210mm]
import { chromium } from 'playwright-core';
import fs from 'node:fs';
import path from 'node:path';

const args = process.argv.slice(2);
const [input, output] = args;
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const pngDir = opt('--png', null);
const scale = parseFloat(opt('--scale', '1.25'));
const width = opt('--width', '297mm'), height = opt('--height', '210mm');
const exe = process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';

const browser = await chromium.launch({ executablePath: exe, args: ['--allow-file-access-from-files', '--font-render-hinting=none'] });
const page = await browser.newPage({ deviceScaleFactor: scale });
await page.goto('file://' + path.resolve(input), { waitUntil: 'load' });
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(400);
const report = await page.evaluate(() => {
  const out = { pages: document.querySelectorAll('.page').length, overflow: [], missingImages: [], fonts: [] };
  document.querySelectorAll('img').forEach(i => { if (!i.complete || i.naturalWidth === 0) out.missingImages.push(i.getAttribute('src')); });
  document.querySelectorAll('.page').forEach((p, k) => {
    p.querySelectorAll('.chk').forEach(el => { if (el.scrollHeight > el.clientHeight + 1 || el.scrollWidth > el.clientWidth + 1) out.overflow.push({ page: k + 1, cls: el.className, text: el.textContent.slice(0, 60) }); });
  });
  document.fonts.forEach(f => out.fonts.push(`${f.family} ${f.weight} ${f.status}`));
  return out;
});
await page.pdf({ path: output, width, height, printBackground: true, preferCSSPageSize: true });
if (pngDir) {
  fs.mkdirSync(pngDir, { recursive: true });
  const n = report.pages;
  for (let k = 0; k < n; k++) {
    const el = (await page.$$('.page'))[k];
    await el.screenshot({ path: path.join(pngDir, `page-${String(k + 1).padStart(2, '0')}.png`) });
  }
}
console.log(JSON.stringify(report, null, 1));
await browser.close();
