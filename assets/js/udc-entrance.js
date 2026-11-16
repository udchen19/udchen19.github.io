// Home entrance ("I solemnly swear…": blank newsprint → the page prints in) and exit
// ("Mischief managed.": the page wipes back to blank paper). Nothing depends on it.
(() => {
  const root = document.documentElement;
  const blocks = () => document.querySelectorAll('body > .page-header, body > .page-body, body > .page-footer');
  const phrase = document.querySelector('[data-udc-phrase]');
  const exitBtn = document.querySelector('[data-udc-exit]');
  if (!phrase) return;
  const end = () => root.classList.remove('udc-entering');
  // Entrance: the class is set before paint by the head hook; finish or skip it.
  if (root.classList.contains('udc-entering')) {
    const skip = () => { end(); off(); };
    const evs = ['keydown', 'pointerdown', 'wheel', 'touchstart', 'scroll'];
    const off = () => evs.forEach(e => removeEventListener(e, skip, true));
    evs.forEach(e => addEventListener(e, skip, { capture: true, passive: true }));
    setTimeout(skip, 900);
  }
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const manage = () => {
    scrollTo({ top: 0, behavior: 'instant' });
    root.classList.add('udc-managed');
    const done = () => { blocks().forEach(b => b.inert = true); phrase.focus({ preventScroll: true }); };
    reduced ? done() : setTimeout(done, 400);
  };
  const restore = () => {
    blocks().forEach(b => b.inert = false);
    root.classList.remove('udc-managed');
    if (!reduced) { root.classList.add('udc-entering', 'udc-reentering'); setTimeout(() => root.classList.remove('udc-entering', 'udc-reentering'), 700); }
    exitBtn?.focus({ preventScroll: true });
    scrollTo({ top: 0, behavior: 'instant' });
  };
  exitBtn?.addEventListener('click', manage);
  phrase.addEventListener('click', () => { if (root.classList.contains('udc-managed')) restore(); });
  // Typing either phrase anywhere works too.
  let typed = '';
  addEventListener('keydown', e => {
    if (e.key.length !== 1 || e.metaKey || e.ctrlKey || e.altKey) return;
    typed = (typed + e.key.toLowerCase()).replace(/[^a-z]/g, '').slice(-64);
    if (typed.endsWith('mischiefmanaged') && !root.classList.contains('udc-managed')) { typed = ''; manage(); }
    else if (/isolemnlyswearthati(am|will)beuptonogood$|isolemnlyswearthatiamuptonogood$/.test(typed) && root.classList.contains('udc-managed')) { typed = ''; restore(); }
  });
})();
