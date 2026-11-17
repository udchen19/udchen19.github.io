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
      tip.setAttribute('aria-live', 'polite'); fig.append(tip);   // outside the plate: it clips and carries the ink mask
      const ports = [...svg.querySelectorAll('.udc-map-port')];
      svg.addEventListener('click', e => {
        const scale = plate.offsetWidth / vb.width;                // CSS px per map unit
        const r = svg.getBoundingClientRect();
        const ux = vb.x + (e.clientX - r.left) / scale, uy = vb.y + (e.clientY - r.top) / scale;
        const reach = 6 / scale;                                   // 6 CSS px, or the dot's own radius
        const near = ports.map(p => ({ p, d: Math.hypot(p.cx.baseVal.value - ux, p.cy.baseVal.value - uy) }))
          .filter(o => o.d <= Math.max(reach, o.p.r.baseVal.value)).sort((a, b) => a.d - b.d).slice(0, 4);
        if (!near.length) { tip.hidden = true; return; }
        tip.textContent = near.map(o => o.p.querySelector('title').textContent).join('\n');
        tip.hidden = false;
        const p0 = near[0].p, half = tip.offsetWidth / 2;
        const x = plate.offsetLeft + (p0.cx.baseVal.value - vb.x) * scale;
        const y = plate.offsetTop + (p0.cy.baseVal.value - vb.y) * scale;
        const below = y - tip.offsetHeight - 10 < 0;
        tip.classList.toggle('is-below', below);
        tip.style.left = Math.min(Math.max(x, half), fig.clientWidth - half) + 'px';
        tip.style.top = y + 'px';
      });
      document.addEventListener('click', e => { if (!svg.contains(e.target)) tip.hidden = true; });
    }
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
