// Entrance test: capture viewport frames at given ms after navigation; optional actions.
import { spawn } from 'node:child_process';
import { writeFileSync, rmSync } from 'node:fs';
const [,, url, outPrefix, mode] = process.argv;
const profile = (process.env.UDC_SCRATCH) + '/chrome-frames'; rmSync(profile, { recursive: true, force: true });
const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', ['--headless=new', '--remote-debugging-port=9334', `--user-data-dir=${profile}`, '--hide-scrollbars', 'about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
for (let i = 0; i < 50; i++) { try { await fetch('http://127.0.0.1:9334/json/version'); break; } catch { await sleep(200); } }
const t = await (await fetch('http://127.0.0.1:9334/json/new?about:blank', { method: 'PUT' })).json();
const ws = new WebSocket(t.webSocketDebuggerUrl); await new Promise(r => ws.addEventListener('open', r, { once: true }));
let id = 0; const pend = new Map(); ws.addEventListener('message', e => { const m = JSON.parse(e.data); if (m.id) { pend.get(m.id)?.(m); pend.delete(m.id); } });
const send = (method, params = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
await send('Page.enable'); await send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 800, deviceScaleFactor: 1, mobile: false });
const shot = async name => { const s = await send('Page.captureScreenshot', { format: 'jpeg', quality: 60 }); writeFileSync(`${outPrefix}-${name}.jpg`, Buffer.from(s.result.data, 'base64')); };
const ev = async expr => (await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true })).result.result.value;
await send('Page.navigate', { url });
const t0 = Date.now();
if (mode === 'frames') { for (const ms of [120, 300, 450, 620, 1100]) { await sleep(Math.max(0, ms - (Date.now() - t0))); await shot(String(ms)); } }
if (mode === 'skip') { await sleep(150); await send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'a', text: 'a' }); await sleep(60); await shot('skip'); console.log('entering after key:', await ev("document.documentElement.classList.contains('udc-entering')")); }
if (mode === 'exit') { await sleep(1300); await ev("document.querySelector('[data-udc-exit]').click()"); await sleep(600); await shot('managed'); console.log('inert:', await ev("document.querySelector('.page-body').inert"), 'focus:', await ev('document.activeElement.className'));
  await ev("document.querySelector('[data-udc-phrase]').click()"); await sleep(900); await shot('restored'); console.log('restored inert:', await ev("document.querySelector('.page-body').inert"));
  await ev("document.querySelector('[data-udc-exit]').click()"); await sleep(600);
  for (const ch of 'i solemnly swear that i am up to no good') await send('Input.dispatchKeyEvent', { type: 'keyDown', key: ch, text: ch });
  await sleep(900); console.log('typed restore managed?', await ev("document.documentElement.classList.contains('udc-managed')")); }
if (mode === 'second') { await sleep(1200); await send('Page.reload'); await sleep(150); console.log('second visit entering:', await ev("document.documentElement.classList.contains('udc-entering')")); }
ws.close(); chrome.kill();
