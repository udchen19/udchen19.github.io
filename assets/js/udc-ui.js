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
    // Keyboard focus that leaves the open menu closes it, so the menu never covers the control in use (Astra, round 16).
    document.addEventListener('focusin', e => {
      if (menuButton?.getAttribute('aria-expanded') === 'true' && !menu?.contains(e.target) && e.target !== menuButton) setMenu(false);
    });
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
      // The button is named by the line showing, so the reply is read too, not only seen (Astra, round 16).
      const named = k => lines.forEach((el, i) => i === k ? el.removeAttribute('aria-hidden') : el.setAttribute('aria-hidden', 'true'));
      const show = k => {
        if (k === showing) return;
        const from = showing; showing = k; cancelAnimationFrame(raf); named(k);
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
      // On touch, the tap decides (a second tap brings the oath back); hover counts only for a mouse (Astra, round 11).
      let lastTouch = false;
      motto.addEventListener('pointerdown', e => { lastTouch = e.pointerType === 'touch'; });
      const want = () => show(managed || (!lastTouch && (motto.matches(':hover') || motto.matches(':focus-visible'))) ? 1 : 0);
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
    // About (plan 4.8; UD 2026-11-16): every lane is a filter. Education and Research start on (UD, 2026-11-17); entries and bars
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
      const map = tl.querySelector('.udc-map');
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
        if (map) map.hidden = !open;   // "Where I've wandered" belongs to life away from the desk (UD, 2026-11-17)
        lifeLanes.forEach(lane => {
          lane.inert = !open;
          lane.querySelector('.udc-ys-filter')?.setAttribute('aria-pressed', String(open));
        });
        apply(); placeVeil();
      };
      // The flap folds away first (instantly with less motion asked for), then the lanes are switched on.
      veil?.addEventListener('click', () => {
        const done = () => { veil.classList.remove('is-lifting'); setLife(true); lifeLanes[0]?.querySelector('.udc-ys-filter')?.focus({ preventScroll: true }); };
        if (matchMedia('(prefers-reduced-motion: reduce)').matches) return done();
        veil.classList.add('is-lifting'); veil.addEventListener('animationend', done, { once: true });
      });
      back?.querySelector('button')?.addEventListener('click', () => { setLife(false); veil?.focus({ preventScroll: true }); });
      addEventListener('resize', placeVeil);
      setLife(false);
      // A link to an entry of a lane that is off turns that lane on, and for a life entry lifts the flap: from a
      // year-strip bar, and when the page is opened at that address (Astra, round 12).
      const showRow = id => {
        const row = id ? document.getElementById(id) : null; if (!row || !row.classList.contains('udc-tl-row')) return null;
        const btn = buttons.find(b => b.dataset.lane === row.dataset.lane);
        if (btn && btn.closest('.udc-ys-life') && wrap?.classList.contains('is-veiled')) setLife(true);
        if (btn && btn.getAttribute('aria-pressed') !== 'true') { btn.setAttribute('aria-pressed', 'true'); apply(); }
        return row;
      };
      // A click on a year-strip mark (or a chooser entry) scrolls down to its entry rather than jumping (UD,
      // 2026-11-17); the address still changes, so the link can be shared and Back returns. Still a jump with
      // reduced motion. Focus moves to the entry, as following the link would.
      document.addEventListener('click', e => {
        const a = e.target.closest('a[href^="#tl-"]');
        if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
        const id = a.getAttribute('href').slice(1), row = showRow(id); if (!row) return;
        e.preventDefault();
        if (location.hash !== '#' + id) history.pushState(null, '', '#' + id);
        row.setAttribute('tabindex', '-1'); row.focus({ preventScroll: true });
        row.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
      });
      const arrive = () => { const row = showRow(decodeURIComponent(location.hash.slice(1))); if (row) requestAnimationFrame(() => row.scrollIntoView()); };
      arrive(); addEventListener('hashchange', arrive);
      // Year-strip marks that sit on one another: a click where several meet offers each of them, the way the
      // flight map lists airports whose dots meet (Astra, round 12).
      const pick = document.createElement('div'); pick.className = 'udc-ys-pick'; pick.hidden = true; pick.setAttribute('role', 'menu');
      tl.querySelector('.udc-ys-wrap')?.append(pick);
      tl.querySelectorAll('.udc-ys-track').forEach(track => track.addEventListener('click', e => {
        const bar = e.target.closest('.udc-ys-bar'); if (!bar || e.detail === 0) return;   // keyboard presses go straight through
        const hits = [...track.querySelectorAll('.udc-ys-bar')].filter(b => { const r = b.getBoundingClientRect(); return e.clientX >= r.left && e.clientX <= r.right; });
        if (hits.length < 2) return;
        e.preventDefault();
        pick.replaceChildren(...hits.map(b => { const a = b.cloneNode(false); a.className = 'udc-ys-pickitem'; a.setAttribute('role', 'menuitem'); a.removeAttribute('style'); a.textContent = b.title; return a; }));
        const wr = pick.parentElement.getBoundingClientRect();
        pick.style.left = Math.min(e.clientX - wr.left, wr.width - 260) + 'px'; pick.style.top = (track.getBoundingClientRect().bottom - wr.top + 4) + 'px';
        pick.origin = bar; pick.hidden = false; pick.querySelector('a')?.focus({ preventScroll: true });
      }));
      // The chooser belongs to its mark: it closes when the strip or page scrolls, the arrow keys move through it,
      // and Escape returns to the mark (Astra, round 13).
      const closePick = back => { if (pick.hidden) return; pick.hidden = true; if (back) pick.origin?.focus({ preventScroll: true }); };
      tl.querySelector('.udc-ys')?.addEventListener('scroll', () => closePick(false), { passive: true });
      addEventListener('scroll', () => closePick(false), { passive: true });
      pick.addEventListener('focusout', e => { if (!pick.contains(e.relatedTarget)) closePick(false); });   // Tab out of it: it closes, focus goes on (round 14)
      pick.addEventListener('keydown', e => {
        const items = [...pick.querySelectorAll('a')], i = items.indexOf(document.activeElement);
        if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); items[(i + (e.key === 'ArrowDown' ? 1 : items.length - 1)) % items.length]?.focus(); }
        if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); closePick(true); }
      });
      pick.addEventListener('click', e => { const a = e.target.closest('a'); if (a) { pick.hidden = true; showRow(a.getAttribute('href').slice(1)); } });
      document.addEventListener('click', e => { if (!pick.hidden && !pick.contains(e.target) && !e.target.closest('.udc-ys-bar')) pick.hidden = true; });
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
      // "What took me there": each event becomes a button that picks its airport, as the list above does (UD, 2026-11-17).
      const evs = [...fig.querySelectorAll('.udc-map-ev')].map(s => {
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
        evs.forEach(b => b.setAttribute('aria-pressed', 'false'));
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
      evs.forEach(b => {
        const pk = picks.find(p => p.dataset.code === b.dataset.code);
        b.addEventListener('click', () => { pk?.click(); b.setAttribute('aria-pressed', 'true'); });
        b.setAttribute('aria-pressed', 'false');
      });
      // As the map unfolds, each place's entry in the key types itself out once the drawing reaches that place,
      // keeping its space until then; the drawing waits for it (times from flightmap.py; UD, 2026-11-16).
      // Without the script, or with less motion asked for, the key is simply there.
      const details = plate.closest('details');
      // Events type out the same way, and as each begins its airport's dot and list entry flash (UD, 2026-11-17).
      const keys = [...fig.querySelectorAll('.udc-map-key > div[data-t], .udc-map-events li[data-t]')].map(div => {
        const chars = [];
        div.querySelectorAll('dt, dd, .udc-map-ev > b, .udc-map-ev-name, .udc-map-ev > i').forEach(el => {
          const text = el.textContent; el.textContent = '';
          for (const ch of text) { const sp = document.createElement('span'); sp.textContent = ch; el.append(sp); chars.push(sp); }
        });
        return { div, t: +div.dataset.t, dur: +div.dataset.dur, chars, code: div.querySelector('.udc-map-ev')?.dataset.code };
      });
      const flash = code => {
        const els = [ports.find(p => p.dataset.code === code), picks.find(p => p.dataset.code === code)?.closest('li')].filter(Boolean);
        els.forEach(el => el.classList.add('is-flash'));
        setTimeout(() => els.forEach(el => el.classList.remove('is-flash')), 900);
      };
      const when = plate.querySelector('.udc-map-when');
      const dates = when ? JSON.parse(when.dataset.dates) : [], end = when ? +when.dataset.end : 0;
      // The date line also names an airport while it first arrives, during its pause (Astra, round 12).
      const whenDate = document.createElement('span'), whenNew = document.createElement('span');
      whenNew.className = 'udc-map-when-new'; when?.append(whenDate, whenNew);
      const named = [...fig.querySelectorAll('.udc-map-ports li')].map(li => ({ t: parseFloat(li.style.getPropertyValue('--t')) || 0,
        name: li.querySelector('b + span')?.firstChild?.textContent.trim() || '' })).filter(x => x.t > 0).sort((a, b) => a.t - b.t);
      const skipBtn = fig.querySelector('.udc-map-skip');
      let typing = 0;
      // While it plays, airports not yet reached in the list can't be focused or chosen (Astra, round 11).
      const listItems = [...fig.querySelectorAll('.udc-map-ports li, .udc-map-events li')].map(li => ({ li, t: parseFloat(li.style.getPropertyValue('--t')) || 0 }));
      const playing = on => {
        details?.classList.toggle('is-playing', on); if (skipBtn) skipBtn.hidden = !on;
        if (!on) listItems.forEach(x => { x.li.inert = false; });
      };
      const skip = () => {
        cancelAnimationFrame(typing); details?.classList.add('is-skipped'); playing(false);
        keys.forEach(k => { k.done = true; k.div.removeAttribute('data-wait'); k.chars.forEach(c => { c.style.visibility = ''; }); });
        if (when) { whenDate.textContent = dates[dates.length - 1]?.[1] || ''; whenNew.textContent = ''; when.classList.add('is-done'); }
      };
      skipBtn?.addEventListener('click', e => { e.stopPropagation(); skip(); });
      // While it plays, a click on the map skips instead of naming an airport (capture: before the map's own handler).
      plate.addEventListener('click', e => { if (details?.classList.contains('is-playing')) { e.stopPropagation(); skip(); } }, true);
      const typeKeys = () => {
        cancelAnimationFrame(typing);
        details?.classList.remove('is-skipped');
        const still = matchMedia('(prefers-reduced-motion: reduce)').matches;
        keys.forEach(k => { const hide = !still && !k.done; k.div.toggleAttribute('data-wait', hide); k.chars.forEach(c => { c.style.visibility = hide ? 'hidden' : ''; }); });
        if (when) { when.hidden = still; when.classList.remove('is-done'); whenDate.textContent = dates[0]?.[1] || ''; whenNew.textContent = ''; }
        if (still) return;
        playing(true);
        listItems.forEach(x => { x.li.inert = x.t > 0; });
        const t0 = performance.now() + 500;
        const frame = now => {
          let busy = false;
          keys.forEach(k => {
            const n = Math.floor(Math.max(0, (now - t0) / 1000 - k.t) / k.dur * k.chars.length);
            if (k.done) return;
            if (n > 0 && k.div.hasAttribute('data-wait')) { k.div.removeAttribute('data-wait'); if (k.code) flash(k.code); }
            k.chars.forEach((c, i) => { if (i < n) c.style.visibility = ''; });
            if (n < k.chars.length) busy = true; else k.done = true;
          });
          const e = (now - t0) / 1000;
          listItems.forEach(x => { if (x.li.inert && e >= x.t) x.li.inert = false; });
          if (when) {
            let d = dates[0]; for (const x of dates) if (x[0] <= e) d = x;
            if (d && whenDate.textContent !== d[1]) whenDate.textContent = d[1];
            let nw = ''; for (const x of named) if (x.t <= e && e < x.t + 1.1) nw = x.name;
            if (whenNew.textContent !== nw) whenNew.textContent = nw;
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
      document.addEventListener('click', e => { if (!svg.contains(e.target) && !e.target.closest('.udc-map-pick, .udc-map-ev')) clear(); });
      document.addEventListener('focusin', e => { if (!e.target.closest('.udc-map-pick, .udc-map-ev') && !svg.contains(e.target)) clear(); });
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
    // Accents, curly quotes and dashes match their plain forms; a short year (’26 or '26) and the full year
    // (2026) are the same, in the text and in what is typed (Astra, round 11).
    const norm = t => t.normalize('NFKD').replace(/[̀-ͯ]/g, '').replace(/[‘’ʼ]/g, "'")
      .replace(/[“”]/g, '"').replace(/[‐-―]/g, '-').toLowerCase().replace(/(^|[^\w])'(\d\d)\b/g, '$1 20$2');
    const words = t => t.split(/[^\p{L}\p{N}]+/u).filter(Boolean);
    const text = new Map(pubs.map(p => [p, norm(p.textContent + ' ' + (p.dataset.search || ''))]));
    const venue = new Map(pubs.map(p => [p, words(norm(p.dataset.venue || ''))]));
    const venueWords = new Set([...venue.values()].flat().filter(w => !/^\d+$/.test(w)));
    let type = '';
    // A year with a venue name ("CHI 2025") searches venues: the venue must hold the names and the paper must be
    // from that year, so a coauthor named Chi does not count; other words still narrow within that. Anything
    // else searches the whole entry.
    const match = (p, qs) => {
      const years = qs.filter(w => /^\d{4}$/.test(w)), rest = qs.filter(w => !/^\d{4}$/.test(w));
      const vw = rest.filter(w => venueWords.has(w)), other = rest.filter(w => !venueWords.has(w));
      // Once the query names a venue and a year, those hold as more words narrow it (Astra, round 12).
      if (years.length && vw.length)
        return years.every(y => p.dataset.year === y) && vw.every(w => venue.get(p).includes(w)) && other.every(w => text.get(p).includes(w));
      return qs.every(w => text.get(p).includes(w));
    };
    const run = () => {
      const qs = norm(q.value).split(/\s+/).filter(Boolean).map(w => w.replace(/^["'(]+|["'),.]+$/g, '')).filter(Boolean);
      let shown = 0;
      pubs.forEach(p => { const ok = (!type || p.dataset.type === type) && match(p, qs); p.hidden = !ok; if (ok) shown++; });
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
