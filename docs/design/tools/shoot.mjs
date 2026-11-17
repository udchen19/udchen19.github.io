// Full-page screenshots through headless Chrome's DevTools protocol (no packages).
// node shoot.mjs <jobs.json>   jobs: [{url, out, width, height, theme: light|dark, mobile, reducedMotion, forcedColors, media, js, eval, print, pdf}]
// print: log the value the eval expression returns (a job with print and no out takes no picture).
// pdf: write out as a US Letter PDF, background graphics off (the browser's default), instead of a picture.
// Each run starts its own Chrome with its own temporary profile and a port Chrome picks, so runs never meet.
import { spawn } from 'node:child_process';
import { readFileSync, writeFileSync, mkdirSync, mkdtempSync, rmSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';

const jobs = JSON.parse(readFileSync(process.argv[2], 'utf8'));
const profile = mkdtempSync(join(process.env.UDC_SCRATCH || tmpdir(), 'chrome-'));
const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', [
  '--headless=new', '--remote-debugging-port=0', `--user-data-dir=${profile}`,
  '--no-first-run', '--hide-scrollbars', '--force-color-profile=srgb', 'about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
const portFile = join(profile, 'DevToolsActivePort');
for (let i = 0; i < 100 && !existsSync(portFile); i++) await sleep(100);
const port = readFileSync(portFile, 'utf8').split('\n')[0];
const target = await (await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: 'PUT' })).json();
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener('open', r, { once: true }));
let id = 0; const pending = new Map(); const events = [];
ws.addEventListener('message', e => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } else events.push(m); });
const send = (method, params = {}) => new Promise(r => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
await send('Page.enable'); await send('Runtime.enable');
for (const j of jobs) {
  const w = j.width, h = j.height || (j.mobile ? 812 : 800);
  await send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: j.scale || (j.mobile ? 2 : 1), mobile: !!j.mobile });
  const feats = [{ name: 'prefers-color-scheme', value: j.theme || 'light' },
    { name: 'prefers-reduced-motion', value: j.reducedMotion ? 'reduce' : 'no-preference' },
    { name: 'forced-colors', value: j.forcedColors ? 'active' : 'none' }];
  await send('Emulation.setEmulatedMedia', { media: j.media || '', features: feats });   // media: 'print' to check print styles
  await send('Emulation.setScriptExecutionDisabled', { value: j.js === false });
  if (j.js === false) { await send('Network.enable'); }
  await send('Network.clearBrowserCookies');
  await send('Page.navigate', { url: j.url });
  await sleep(j.wait || 1800);
  if (j.js !== false) await send('Runtime.evaluate', { expression: "document.querySelector('.udc-dev')?.remove(); document.head.insertAdjacentHTML('beforeend', '<style>.udc-home > * { content-visibility: visible !important; }</style>'); window.scrollTo(0, document.body.scrollHeight); new Promise(r => setTimeout(r, 400)).then(() => { window.scrollTo(0, 0); return document.fonts.ready; })", awaitPromise: true });
  if (j.eval) {
    const r = await send('Runtime.evaluate', { expression: j.eval, awaitPromise: true, returnByValue: true });
    if (j.print) console.log(JSON.stringify(r.result.result?.value ?? r.result.exceptionDetails?.text));
  }
  if (j.print && !j.out) continue;
  await sleep(300);
  const m = await send('Page.getLayoutMetrics');
  const ch = Math.ceil(m.result.cssContentSize.height);
  let clip = { x: 0, y: 0, width: w, height: j.fullPage === false ? h : ch, scale: 1 };
  if (j.selector) {
    const r = await send('Runtime.evaluate', { expression: `(() => { const b = document.querySelectorAll(${JSON.stringify(j.selector)})[${j.index || 0}].getBoundingClientRect(); return JSON.stringify({x: b.x + scrollX, y: b.y + scrollY, width: b.width, height: b.height}); })()`, returnByValue: true });
    clip = { ...JSON.parse(r.result.result.value), scale: 1 };
  }
  if (j.pdf) {
    const pdf = await send('Page.printToPDF', { printBackground: false, paperWidth: 8.5, paperHeight: 11 });
    mkdirSync(dirname(j.out), { recursive: true });
    writeFileSync(j.out, Buffer.from(pdf.result.data, 'base64'));
    console.log('pdf', j.out); continue;
  }
  const shot = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true, clip });
  mkdirSync(dirname(j.out), { recursive: true });
  writeFileSync(j.out, Buffer.from(shot.result.data, 'base64'));
  console.log('shot', j.out, w + 'x' + ch);
}
ws.close(); chrome.kill(); await sleep(300); rmSync(profile, { recursive: true, force: true });
