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
    // Flight map: a tap or click on a dot shows its airport (hover alone does not exist on phones).
    // Place dots sit on airport dots; a tap there shows the airport under it.
    const plate = document.querySelector('.udc-map-plate');
    if (plate) {
      const svg = plate.querySelector('svg'); const vb = svg.viewBox.baseVal;
      const tip = document.createElement('p'); tip.className = 'udc-map-tip'; tip.hidden = true;
      tip.setAttribute('aria-live', 'polite'); plate.parentElement.append(tip);   // outside the plate: it clips and carries the ink mask
      const ports = [...svg.querySelectorAll('.udc-map-port')];
      svg.addEventListener('click', e => {
        const c = e.target.closest('circle'); if (!c) { tip.hidden = true; return; }
        const port = c.classList.contains('udc-map-port') ? c
          : ports.find(p => p.getAttribute('cx') === c.getAttribute('cx') && p.getAttribute('cy') === c.getAttribute('cy'));
        if (!port) return;
        tip.textContent = port.querySelector('title').textContent;
        tip.hidden = false;
        // Centred over the dot, but kept inside the figure (dots near an edge would push it out).
        const fig = plate.parentElement.clientWidth, half = tip.offsetWidth / 2;
        const x = plate.offsetLeft + (port.cx.baseVal.value - vb.x) / vb.width * plate.offsetWidth;
        tip.style.left = Math.min(Math.max(x, half), fig - half) + 'px';
        tip.style.top = plate.offsetTop + (port.cy.baseVal.value - vb.y) / vb.height * plate.offsetHeight + 'px';
      });
      document.addEventListener('click', e => { if (!svg.contains(e.target)) tip.hidden = true; });
    }
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
