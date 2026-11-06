#!/usr/bin/env node
// Check every slide of a built Wrapped page on small phone screens, in light and dark mode.
//
// Usage: node scripts/check_layout.mjs out.html [screenshot-dir]
//
// Needs Playwright with Chromium. Exits 1 if any slide overflows (text running into the
// Back/Next buttons, off the bottom, or off the side) even after the page's auto-fit.
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
import fs from 'node:fs';
import path from 'node:path';

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); } catch {
  console.log('Playwright is not installed; skipping. The page still auto-shrinks text to fit.');
  process.exit(0);
}

const [file, shotDir] = process.argv.slice(2);
if (!file) { console.log('usage: node check_layout.mjs out.html [screenshot-dir]'); process.exit(2); }
const url = pathToFileURL(path.resolve(file)).href;
if (shotDir) fs.mkdirSync(shotDir, { recursive: true });

// 375x667 is the target: overflow there is a failure. 320x568 is a smaller-phone advisory.
const viewports = [
  { name: '375x667', width: 375, height: 667, required: true },
  { name: '320x568', width: 320, height: 568, required: false },
];
const TIGHT = 0.88; // auto-fit had to shrink text below this: trim the copy
let browser;
try { browser = await chromium.launch(); }
catch { browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' }); }

let problems = 0;
let advisories = 0;
for (const vp of viewports) {
  for (const scheme of ['light', 'dark']) {
    const page = await browser.newPage({ viewport: { width: vp.width, height: vp.height }, colorScheme: scheme });
    const errors = [];
    page.on('pageerror', (e) => errors.push(e.message));
    await page.goto(url);
    await page.waitForTimeout(600); // fonts + auto-fit
    const report = await page.evaluate(() => {
      const ctrl = document.querySelector('.controls').getBoundingClientRect();
      return [...document.querySelectorAll('.slide')].map((s, i) => {
        const c = s.querySelector('.content').getBoundingClientRect();
        const kids = [...s.querySelectorAll('.content *')].map((n) => n.getBoundingClientRect());
        const right = Math.max(...kids.map((r) => r.right), c.right);
        return {
          slide: i + 1,
          type: s.dataset.type,
          scale: Number(s.dataset.fs),
          bottom: Math.round(c.bottom),
          limit: Math.round(ctrl.top),
          overflowX: right > window.innerWidth + 1,
          overflowY: c.bottom > ctrl.top - 4,
        };
      });
    });
    for (const r of report) {
      const bad = r.overflowX || r.overflowY;
      const tight = !bad && r.scale < TIGHT;
      if (bad && vp.required) problems++;
      else if (bad || (tight && vp.required)) advisories++;
      const flag = bad ? (vp.required ? 'OVERFLOW (trim copy)' : 'overflow on small phones (advisory)')
        : tight ? `tight, shrunk to ${r.scale}${vp.required ? ' (trim copy)' : ''}`
        : r.scale < 1 ? `shrunk to ${r.scale}` : 'ok';
      console.log(`${vp.name} ${scheme.padEnd(5)} slide ${String(r.slide).padStart(2)} ${r.type.padEnd(11)} ${flag}`);
    }
    if (errors.length) { problems++; console.log('page errors:', errors); }
    if (shotDir) {
      const n = report.length;
      for (let i = 0; i < n; i++) {
        await page.screenshot({ path: path.join(shotDir, `${vp.name}-${scheme}-${String(i + 1).padStart(2, '0')}.png`) });
        await page.keyboard.press('ArrowRight');
        await page.waitForTimeout(450);
      }
    }
    await page.close();
  }
}
await browser.close();
console.log(problems ? `\n${problems} problem(s) found` : '\nAll slides fit at 375x667.');
if (advisories) console.log(`${advisories} advisory note(s): consider trimming those slides.`);
process.exit(problems ? 1 : 0);
