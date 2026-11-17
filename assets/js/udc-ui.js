// Menu toggle, theme-button labels and the motto's tap state. Without this script the motto still
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
    motto?.addEventListener('pointerup', e => { if (e.pointerType === 'touch') motto.classList.toggle('is-managed'); });
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
      const reveal = tl.querySelector('.udc-ys-reveal');
      const lifeLanes = [...tl.querySelectorAll('.udc-ys-life')];
      const setLife = open => {
        reveal?.setAttribute('aria-expanded', String(open));
        lifeLanes.forEach(lane => {
          lane.hidden = !open;
          lane.querySelector('.udc-ys-filter')?.setAttribute('aria-pressed', String(open));
        });
        apply();
      };
      reveal?.addEventListener('click', () => setLife(reveal.getAttribute('aria-expanded') !== 'true'));
      setLife(false);
      // A link to an entry of a lane that is off (from a year-strip bar or the map) turns that lane on.
      document.addEventListener('click', e => {
        const a = e.target.closest('a[href^="#tl-"]'); if (!a) return;
        const row = document.getElementById(a.getAttribute('href').slice(1));
        const btn = row && buttons.find(b => b.dataset.lane === row.dataset.lane);
        if (btn && btn.closest('.udc-ys-life')?.hidden) setLife(true);
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
    // The section list: always open beside the text; folded under the date on narrower screens.
    const toc = document.querySelector('.udc-toc-fold');
    if (toc) { const set = () => { toc.open = wide.matches; }; set(); wide.addEventListener('change', set); }
  };
  const start = () => { init(); newsFade(); unfold(); };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
