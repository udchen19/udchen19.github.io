import { spawn } from 'node:child_process'; import { rmSync } from 'node:fs';
const [,, url, w] = process.argv; const profile = process.env.UDC_SCRATCH + '/chrome-w'; rmSync(profile, { recursive: true, force: true });
const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', ['--headless=new', '--remote-debugging-port=9335', `--user-data-dir=${profile}`, 'about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
for (let i = 0; i < 50; i++) { try { await fetch('http://127.0.0.1:9335/json/version'); break; } catch { await sleep(200); } }
const t = await (await fetch('http://127.0.0.1:9335/json/new?about:blank', { method: 'PUT' })).json();
const ws = new WebSocket(t.webSocketDebuggerUrl); await new Promise(r => ws.addEventListener('open', r, { once: true }));
let id = 0; const pend = new Map(); ws.addEventListener('message', e => { const m = JSON.parse(e.data); if (m.id) { pend.get(m.id)?.(m); pend.delete(m.id); } });
const send = (method, params = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
await send('Page.enable'); await send('Emulation.setDeviceMetricsOverride', { width: +w, height: 800, deviceScaleFactor: 1, mobile: +w < 760 });
await send('Page.navigate', { url }); await sleep(2500);
const r = await send('Runtime.evaluate', { expression: `JSON.stringify(performance.getEntriesByType('resource').map(e => [e.name.split('/').pop(), e.initiatorType, Math.round(e.encodedBodySize/1024)]))`, returnByValue: true });
const list = JSON.parse(r.result.result.value);
const fonts = list.filter(x => /woff2/.test(x[0])), tex = list.filter(x => /\.(png|webp|jpg)/.test(x[0]));
console.log('fonts', fonts.reduce((a, x) => a + x[2], 0), 'KB:', fonts.map(x => x[0] + ' ' + x[2]).join(', '));
console.log('images/textures', tex.reduce((a, x) => a + x[2], 0), 'KB');
ws.close(); chrome.kill();
