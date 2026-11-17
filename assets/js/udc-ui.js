// Menu toggle, theme-button labels and the motto's ink dissolve. Without this script the motto still
// answers hover and keyboard focus.
(() => {
  const root = document.documentElement;
  const init = () => {
    const themeButtons = document.querySelectorAll('.udc-theme-toggle');
    const menuButton = document.querySelector('.udc-menu-toggle');
    const menu = document.querySelector('#udc-navigation');
    const motto = document.querySelector('.udc-motto');
    const label = () => {
      const dark = root.classList.contains('dark');
      themeButtons.forEach(b => {
        b.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
        b.setAttribute('aria-pressed', String(dark));
      });
      const open = menuButton?.getAttribute('aria-expanded') === 'true';
      menuButton?.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    };
    const setMenu = open => {
      menuButton?.setAttribute('aria-expanded', String(open));
      menu?.classList.toggle('is-open', open);
      label();
    };
    menuButton?.addEventListener('click', () => setMenu(menuButton.getAttribute('aria-expanded') !== 'true'));
    // The head script hides the phone menu only while this handler exists (see hooks/head-end/udc.html).
    window.udcMenuReady = true;
    root.classList.add('udc-js');
    menu?.querySelectorAll('a').forEach(link => link.addEventListener('click', () => setMenu(false)));
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && menuButton?.getAttribute('aria-expanded') === 'true') { setMenu(false); menuButton.focus(); }
    });
    document.addEventListener('click', e => { if (!e.target.closest('.udc-masthead')) setMenu(false); });
    matchMedia('(min-width: 641px)').addEventListener('change', () => setMenu(false));
    new MutationObserver(label).observe(root, { attributes: true, attributeFilter: ['class'] });
    label();
    // Motto (plan 4.2): hover and focus are CSS; on touch a tap toggles the state.
    // Motto (UD, 2026-11-16): the line dissolves into ink specks where it stands and the other soaks back in.
    // Each line runs through an SVG noise filter whose threshold is moved frame by frame; at rest no filter.
    if (motto) {
      const lines = [...motto.querySelectorAll(':scope > span')];
      const ns = 'http://www.w3.org/2000/svg';
      const svg = document.createElementNS(ns, 'svg');
      svg.setAttribute('aria-hidden', 'true'); svg.style.cssText = 'position:absolute;width:0;height:0;overflow:hidden';
      svg.innerHTML = lines.map((_, i) => `<filter id="udc-ink-${i}" x="0" y="-25%" width="100%" height="150%" color-interpolation-filters="sRGB">
        <feTurbulence type="fractalNoise" baseFrequency="0.32" numOctaves="2" seed="${7 + i}" result="n"/>
        <feColorMatrix in="n" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0" result="a"/>
        <feComponentTransfer in="a" result="m"><feFuncA type="linear" slope="9" intercept="0"/></feComponentTransfer>
        <feComposite in="SourceGraphic" in2="m" operator="in"/></filter>`).join('');
      document.body.append(svg);
      const funcs = [...svg.querySelectorAll('feFuncA')];
      const still = matchMedia('(prefers-reduced-motion: reduce)');
      // ink(i, t): t = 0 fully printed, 1 gone. The noise sits roughly between .2 and .8.
      const ink = (i, t) => {
        const el = lines[i];
        if (t <= 0) { el.style.filter = ''; el.style.opacity = 1; return; }
        if (t >= 1) { el.style.filter = ''; el.style.opacity = 0; return; }
        const th = .15 + t * .7;
        funcs[i].setAttribute('intercept', String(-9 * th));
        el.style.filter = `url(#udc-ink-${i})`; el.style.opacity = 1;
      };
      let showing = 0, raf = 0;
      ink(0, 0); ink(1, 1);
      const show = k => {
        if (k === showing) return;
        const from = showing; showing = k; cancelAnimationFrame(raf);
        if (still.matches) { ink(from, 1); ink(k, 0); return; }
        const t0 = performance.now(), out = 480, inn = 620, lag = 320;
        const step = now => {
          const e = now - t0;
          ink(from, Math.min(1, e / out));
          ink(k, 1 - Math.min(1, Math.max(0, (e - lag) / inn)));
          if (e < lag + inn) raf = requestAnimationFrame(step);
        };
        raf = requestAnimationFrame(step);
      };
      let managed = false;
      const want = () => show(managed || motto.matches(':hover') || motto.matches(':focus-visible') ? 1 : 0);
      motto.addEventListener('pointerenter', e => { if (e.pointerType !== 'touch') want(); });
      motto.addEventListener('pointerleave', e => { if (e.pointerType !== 'touch') want(); });
      motto.addEventListener('focus', () => setTimeout(want));
      motto.addEventListener('blur', () => setTimeout(want));
      motto.addEventListener('pointerup', e => { if (e.pointerType === 'touch') { managed = !managed; want(); } });
    }
    // Dateline (UD, 2026-11-16): the reader's own date, British style: "Monday, 16th November 2026".
    const date = document.querySelector('.udc-date');
    const setDate = () => {
      const d = new Date(), n = d.getDate();
      const th = n % 100 >= 11 && n % 100 <= 13 ? 'th' : ({ 1: 'st', 2: 'nd', 3: 'rd' }[n % 10] || 'th');
      const part = o => d.toLocaleDateString('en-GB', o);
      date.textContent = `${part({ weekday: 'long' })}, ${n}${th} ${part({ month: 'long' })} ${d.getFullYear()}`;
      date.dateTime = [d.getFullYear(), d.getMonth() + 1, n].map((v, i) => String(v).padStart(i ? 2 : 4, '0')).join('-');
      date.hidden = false;
      // Turn over at the reader's midnight, and when a tab that slept past it is shown again (Astra, round 8).
      clearTimeout(setDate.t);
      setDate.t = setTimeout(setDate, new Date(d.getFullYear(), d.getMonth(), n + 1) - d + 1000);
    };
    if (date) {
      setDate();
      document.addEventListener('visibilitychange', () => { if (!document.hidden) setDate(); });
    }
    // About (plan 4.8; UD 2026-11-16): every lane is a filter. Work lanes start on; entries and bars
    // of lanes that are off are hidden. The life lanes stay out of sight until "Away from the desk" is
    // pressed, which shows them switched on; pressing it again hides them. Without this script
    // everything shows.
    // The year strip opens at its newest end when it is wider than the page.
    const ys = document.querySelector('.udc-ys');
    if (ys) ys.scrollLeft = ys.scrollWidth;
    const tl = document.querySelector('[data-udc-tl]');
    if (tl) {
      const buttons = [...tl.querySelectorAll('.udc-ys-filter')];
      const apply = () => {
        const on = new Set(buttons.filter(b => b.getAttribute('aria-pressed') === 'true').map(b => b.dataset.lane));
        tl.querySelectorAll('.udc-tl-row[data-lane], .udc-ys-lane[data-lane]').forEach(el =>
          el.classList.toggle('is-off', !on.has(el.dataset.lane)));
      };
      buttons.forEach(b => b.addEventListener('click', () => {
        b.setAttribute('aria-pressed', String(b.getAttribute('aria-pressed') !== 'true')); apply();
      }));
      // "Away from the desk?" (UD, 2026-11-16): the life lanes lie blurred under a veil; lifting it shows them and
      // their entries in the list; "Back to the desk" puts the veil back and takes the entries out again.
      const wrap = tl.querySelector('.udc-ys-wrap');
      const veil = tl.querySelector('.udc-ys-veil'), back = tl.querySelector('.udc-ys-back');
      const lifeLanes = [...tl.querySelectorAll('.udc-ys-life')];
      const placeVeil = () => {
        if (!veil || !lifeLanes.length) return;
        const top = lifeLanes[0].offsetTop, last = lifeLanes[lifeLanes.length - 1];
        veil.style.top = top + 'px'; veil.style.height = (last.offsetTop + last.offsetHeight - top) + 'px';
      };
      const setLife = open => {
        veil?.setAttribute('aria-expanded', String(open));
        wrap?.classList.toggle('is-veiled', !open);
        if (veil) veil.hidden = open;
        if (back) back.hidden = !open;
        lifeLanes.forEach(lane => {
          lane.inert = !open;
          lane.querySelector('.udc-ys-filter')?.setAttribute('aria-pressed', String(open));
        });
        apply(); placeVeil();
      };
      veil?.addEventListener('click', () => { setLife(true); lifeLanes[0]?.querySelector('.udc-ys-filter')?.focus({ preventScroll: true }); });
      back?.querySelector('button')?.addEventListener('click', () => { setLife(false); veil?.focus({ preventScroll: true }); });
      addEventListener('resize', placeVeil);
      setLife(false);
      // A link to an entry of a lane that is off (from a year-strip bar or the map) turns that lane on.
      document.addEventListener('click', e => {
        const a = e.target.closest('a[href^="#tl-"]'); if (!a) return;
        const row = document.getElementById(a.getAttribute('href').slice(1));
        const btn = row && buttons.find(b => b.dataset.lane === row.dataset.lane);
        if (btn && btn.closest('.udc-ys-life') && wrap?.classList.contains('is-veiled')) setLife(true);
        if (btn && btn.getAttribute('aria-pressed') !== 'true') { btn.setAttribute('aria-pressed', 'true'); apply(); }
      });
    }
    // Flight map: a tap or click shows the airport under it (hover alone does not exist on phones).
    // Airports can sit a few px apart (London's three, Taipei's two), so the label lists the airports whose
    // dots meet the tap point (up to four, nearest first) instead of naming whichever dot is drawn on top.
    // It sits above the dot, or below when there is no room above; it never leaves the figure.
    const plate = document.querySelector('.udc-map-plate');
    if (plate) {
      const svg = plate.querySelector('svg'); const vb = svg.viewBox.baseVal; const fig = plate.parentElement;
      const tip = document.createElement('p'); tip.className = 'udc-map-tip'; tip.hidden = true;
      tip.setAttribute('aria-live', 'polite'); plate.after(tip);   // outside the plate: it clips and carries the ink mask
      const ports = [...svg.querySelectorAll('.udc-map-port')];
      const ring = svg.querySelector('.udc-map-ring');
      // The list is plain text without this script; here each entry becomes a button (Astra, round 7).
      const picks = [...fig.querySelectorAll('.udc-map-pick')].map(s => {
        const b = document.createElement('button'); b.type = 'button'; b.className = s.className;
        b.dataset.code = s.dataset.code; b.append(...s.childNodes); s.replaceWith(b); return b;
      });
      let shown = null;                                            // the airports the open label names
      // The ring clears the orange place dots (r 8 in map units) by 4 CSS px, at any width.
      const ringR = () => 8 + 4 * vb.width / plate.offsetWidth;
      const clear = () => {
        tip.hidden = true; shown = null;
        ring?.setAttribute('visibility', 'hidden');
        ports.forEach(p => p.classList.remove('is-on'));
        picks.forEach(b => b.setAttribute('aria-pressed', 'false'));
      };
      // Label for one or more airports, placed by the first: above its dot, or below when there is no room.
      const show = list => {
        const scale = plate.offsetWidth / vb.width;
        shown = list;
        tip.textContent = list.map(p => p.querySelector('title').textContent).join('\n');
        tip.hidden = false;
        const p0 = list[0], half = tip.offsetWidth / 2;
        const x = plate.offsetLeft + (p0.cx.baseVal.value - vb.x) * scale;
        const y = plate.offsetTop + (p0.cy.baseVal.value - vb.y) * scale;
        tip.classList.toggle('is-below', y - tip.offsetHeight - 10 < 0);
        tip.style.left = Math.min(Math.max(x, half), fig.clientWidth - half) + 'px';
        tip.style.top = y + 'px';
      };
      svg.addEventListener('click', e => {
        clear();
        const scale = plate.offsetWidth / vb.width;                // CSS px per map unit
        const r = svg.getBoundingClientRect();
        const ux = vb.x + (e.clientX - r.left) / scale, uy = vb.y + (e.clientY - r.top) / scale;
        const reach = 6 / scale;                                   // 6 CSS px, or the dot's own radius
        const near = ports.map(p => ({ p, d: Math.hypot(p.cx.baseVal.value - ux, p.cy.baseVal.value - uy) }))
          .filter(o => o.d <= Math.max(reach, o.p.r.baseVal.value)).sort((a, b) => a.d - b.d).slice(0, 4);
        if (near.length) show(near.map(o => o.p));
      });
      // The airport list: focus or press marks one airport's dot and shows its label (keyboard and
      // screen readers; also picks one airport where dots overlap).
      picks.forEach(b => {
        const port = ports.find(p => p.dataset.code === b.dataset.code);
        b.setAttribute('aria-pressed', 'false');
        const pick = () => {
          clear(); port.classList.add('is-on'); b.setAttribute('aria-pressed', 'true'); show([port]);
          ring?.setAttribute('cx', port.cx.baseVal.value); ring?.setAttribute('cy', port.cy.baseVal.value);
          ring?.setAttribute('r', ringR());
          ring?.setAttribute('visibility', 'visible');
        };
        b.addEventListener('focus', pick);
        // Pressing (Enter, Space or a click) also brings the map and its label into view; moving with Tab does not (Astra, round 8).
        b.addEventListener('click', () => {
          pick();
          const top = plate.getBoundingClientRect().top, bottom = Math.max(plate.getBoundingClientRect().bottom, tip.getBoundingClientRect().bottom);
          if (top < 0 || bottom > innerHeight) scrollBy({ top: top - 16, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
        });
      });
      // As the map unfolds, each place's entry in the key types itself out once the drawing reaches that place,
      // keeping its space until then; the drawing waits for it (times from flightmap.py; UD, 2026-11-16).
      // Without the script, or with less motion asked for, the key is simply there.
      const details = plate.closest('details');
      const keys = [...fig.querySelectorAll('.udc-map-key > div[data-t]')].map(div => {
        const chars = [];
        div.querySelectorAll('dt, dd').forEach(el => {
          const text = el.textContent; el.textContent = '';
          for (const ch of text) { const sp = document.createElement('span'); sp.textContent = ch; el.append(sp); chars.push(sp); }
        });
        return { div, t: +div.dataset.t, dur: +div.dataset.dur, chars };
      });
      const when = plate.querySelector('.udc-map-when');
      const dates = when ? JSON.parse(when.dataset.dates) : [], end = when ? +when.dataset.end : 0;
      const skipBtn = plate.querySelector('.udc-map-skip');
      let typing = 0;
      const playing = on => { details?.classList.toggle('is-playing', on); if (skipBtn) skipBtn.hidden = !on; };
      const skip = () => {
        cancelAnimationFrame(typing); details?.classList.add('is-skipped'); playing(false);
        keys.forEach(k => { k.done = true; k.div.removeAttribute('data-wait'); k.chars.forEach(c => { c.style.visibility = ''; }); });
        if (when) { when.textContent = dates[dates.length - 1]?.[1] || ''; when.classList.add('is-done'); }
      };
      skipBtn?.addEventListener('click', e => { e.stopPropagation(); skip(); });
      // While it plays, a click on the map skips instead of naming an airport (capture: before the map's own handler).
      plate.addEventListener('click', e => { if (details?.classList.contains('is-playing')) { e.stopPropagation(); skip(); } }, true);
      const typeKeys = () => {
        cancelAnimationFrame(typing);
        details?.classList.remove('is-skipped');
        const still = matchMedia('(prefers-reduced-motion: reduce)').matches;
        keys.forEach(k => { const hide = !still && !k.done; k.div.toggleAttribute('data-wait', hide); k.chars.forEach(c => { c.style.visibility = hide ? 'hidden' : ''; }); });
        if (when) { when.hidden = still; when.classList.remove('is-done'); when.textContent = dates[0]?.[1] || ''; }
        if (still) return;
        playing(true);
        const t0 = performance.now() + 500;
        const frame = now => {
          let busy = false;
          keys.forEach(k => {
            const n = Math.floor(Math.max(0, (now - t0) / 1000 - k.t) / k.dur * k.chars.length);
            if (k.done) return;
            if (n > 0) k.div.removeAttribute('data-wait');
            k.chars.forEach((c, i) => { if (i < n) c.style.visibility = ''; });
            if (n < k.chars.length) busy = true; else k.done = true;
          });
          const e = (now - t0) / 1000;
          if (when) {
            let d = dates[0]; for (const x of dates) if (x[0] <= e) d = x;
            if (d && when.textContent !== d[1]) when.textContent = d[1];
            if (e > end + .6) when.classList.add('is-done'); else busy = true;
          }
          if (busy) typing = requestAnimationFrame(frame); else playing(false);
        };
        typing = requestAnimationFrame(frame);
      };
      // The journey plays on the first opening after the page loads; later openings show the map finished (UD).
      let played = false;
      details?.addEventListener('toggle', () => {
        if (!details.open) { cancelAnimationFrame(typing); playing(false); return; }
        if (played) skip(); else { played = true; typeKeys(); }
      });
      // When the map changes size (rotation, window), the open label and ring follow their dot (Astra, round 7).
      new ResizeObserver(() => {
        if (!shown) return;
        show(shown);
        if (ring?.getAttribute('visibility') === 'visible') ring.setAttribute('r', ringR());
      }).observe(plate);
      document.addEventListener('click', e => { if (!svg.contains(e.target) && !e.target.closest('.udc-map-pick')) clear(); });
      document.addEventListener('focusin', e => { if (!e.target.closest('.udc-map-pick') && !svg.contains(e.target)) clear(); });
    }
  };
  // Sections list (article pages): choosing a section also opens its folded part, if it has one; the page
  // still arrives folded (Astra, round 8).
  document.addEventListener('click', e => {
    const a = e.target.closest('.udc-toc a'); if (!a) return;
    const h = document.getElementById(decodeURIComponent(a.hash.slice(1)));
    for (let n = h?.nextElementSibling; n && !/^H[1-3]$/.test(n.tagName); n = n.nextElementSibling)
      if (n.tagName === 'DETAILS') { n.open = true; break; }
  });
  // News: while more entries wait below, the last visible line fades (UD).
  const newsFade = () => document.querySelectorAll('.udc-news-list').forEach(l =>
    l.classList.toggle('has-more', l.scrollTop + l.clientHeight < l.scrollHeight - 2));
  document.addEventListener('scroll', e => { if (e.target.classList?.contains('udc-news-list')) newsFade(); }, true);
  addEventListener('resize', newsFade);
  // Folds in posts (UD, 2026-11-16; Astra, round 9). From 900px, where the section list sits beside the text,
  // the author's whole-section folds ("展開本節") open on arrival; folds the author labelled as detours (such as
  // "7500+字 慎入") stay folded until chosen. A whole-section fold's label says what pressing it does.
  const wide = matchMedia('(min-width: 900px)');
  const sectionFold = d => /^(展開|收合)本節$/.test(d.querySelector(':scope > summary')?.textContent.trim() || '');
  const label = d => { const s = d.querySelector(':scope > summary'); if (s && sectionFold(d)) s.textContent = d.open ? '收合本節' : '展開本節'; };
  const unfold = () => {
    document.querySelectorAll('.udc-prose details').forEach(d => {
      if (wide.matches && sectionFold(d)) d.open = true;
      label(d);
      d.addEventListener('toggle', () => label(d));
    });
    // A link to a section or a passage opens the fold that holds it, whether it came from the list or
    // from another reader (Astra, round 10); other folds stay as the author set them.
    const reveal = () => {
      const t = location.hash && document.getElementById(decodeURIComponent(location.hash.slice(1)));
      if (!t) return;
      for (let d = t.closest('details'); d; d = d.parentElement.closest('details')) d.open = true;
      if (/^H[2-4]$/.test(t.tagName)) for (let n = t.nextElementSibling; n && !/^H[1-3]$/.test(n.tagName); n = n.nextElementSibling)
        if (n.tagName === 'DETAILS') { n.open = true; break; }
      t.scrollIntoView();
    };
    reveal(); addEventListener('hashchange', reveal);
    // The section list: always open beside the text; folded under the date on narrower screens.
    const toc = document.querySelector('.udc-toc-fold');
    if (toc) {
      // Beside the text it is a plain heading: always open, not focusable, not toggled by click or key (Astra, round 10).
      const sum = toc.querySelector('summary');
      const set = () => { toc.open = wide.matches; sum.tabIndex = wide.matches ? -1 : 0; };
      sum.addEventListener('click', e => { if (wide.matches) e.preventDefault(); });
      toc.addEventListener('toggle', () => { if (wide.matches && !toc.open) toc.open = true; });
      set(); wide.addEventListener('change', set);
    }
  };
  // Publications filter (UD, 2026-11-16): typing matches title, authors and venue; a type button shows one
  // type; years with nothing left hide, and a line says what is shown.
  const pubFilter = () => {
    const form = document.querySelector('.udc-pubfilter'); if (!form) return;
    const q = form.querySelector('.udc-pubfilter-q'), btns = [...form.querySelectorAll('.udc-pubfilter-type')];
    const status = form.querySelector('.udc-pubfilter-status'), pubs = [...document.querySelectorAll('.udc-pub')];
    // Accents, curly quotes and dashes match their plain forms; a short year (’26) also matches 2026.
    const norm = t => t.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').replace(/[\u2018\u2019\u02bc]/g, "'")
      .replace(/[\u201c\u201d]/g, '"').replace(/[\u2010-\u2015]/g, '-').toLowerCase();
    const text = new Map(pubs.map(p => [p, norm(p.textContent + ' ' + (p.dataset.search || '')).replace(/'(\d\d)\b/g, " 20$1")]));
    let type = '';
    const run = () => {
      const words = norm(q.value).split(/\s+/).filter(Boolean);
      let shown = 0;
      pubs.forEach(p => { const ok = (!type || p.dataset.type === type) && words.every(w => text.get(p).includes(w)); p.hidden = !ok; if (ok) shown++; });
      document.querySelectorAll('.udc-year').forEach(y => { y.hidden = !y.querySelector('.udc-pub:not([hidden])'); });
      status.textContent = (q.value || type) ? (shown ? `${shown} of ${pubs.length} shown` : 'Nothing matches.') : '';
    };
    btns.forEach(b => b.addEventListener('click', () => { type = b.dataset.type; btns.forEach(x => x.setAttribute('aria-pressed', String(x === b))); run(); }));
    q.addEventListener('input', run);
    form.addEventListener('submit', e => e.preventDefault());
    form.hidden = false;
  };
  const start = () => { init(); newsFade(); unfold(); pubFilter(); };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
