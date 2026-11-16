import { spawn } from 'node:child_process'; import { rmSync } from 'node:fs';
const [,, url, w] = process.argv; const profile = process.env.UDC_SCRATCH + '/chrome-c'; rmSync(profile, { recursive: true, force: true });
const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', ['--headless=new', '--remote-debugging-port=9336', `--user-data-dir=${profile}`, 'about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
for (let i = 0; i < 50; i++) { try { await fetch('http://127.0.0.1:9336/json/version'); break; } catch { await sleep(200); } }
const t = await (await fetch('http://127.0.0.1:9336/json/new?about:blank', { method: 'PUT' })).json();
const ws = new WebSocket(t.webSocketDebuggerUrl); await new Promise(r => ws.addEventListener('open', r, { once: true }));
let id = 0; const pend = new Map(); ws.addEventListener('message', e => { const m = JSON.parse(e.data); if (m.id) { pend.get(m.id)?.(m); pend.delete(m.id); } });
const send = (method, params = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
await send('Page.enable'); await send('Emulation.setDeviceMetricsOverride', { width: +w, height: 800, deviceScaleFactor: 1, mobile: +w < 760 });
await send('Page.navigate', { url }); await sleep(2500);
const r = await send('Runtime.evaluate', { expression: `JSON.stringify((() => { const d = document.documentElement; const ft = document.querySelector('.udc-field-text'); const fs = parseFloat(getComputedStyle(ft).fontSize); const clipped = [...ft.querySelectorAll('span')].concat([ft]).some(e => e.scrollWidth > e.clientWidth + 1) || ft.getBoundingClientRect().right > document.querySelector('.udc-field').getBoundingClientRect().right + 1; const over = [...document.querySelectorAll('body *')].filter(e => { const b = e.getBoundingClientRect(); return b.width && (b.right > innerWidth + 1) && getComputedStyle(e).position !== 'fixed'; }).slice(0, 4).map(e => e.tagName + '.' + String(e.className).slice(0, 30)); return { hscroll: d.scrollWidth > d.clientWidth, fieldPx: fs, fieldH: Math.round(document.querySelector('.udc-field').getBoundingClientRect().height), clipped, over }; })())`, returnByValue: true });
console.log(url, w, r.result.result.value);
ws.close(); chrome.kill();
