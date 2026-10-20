(() => {
  const root = document.documentElement;
  const labels = {
    research: { en: 'Research', zh: '研究' },
    publications: { en: 'Publications', zh: '出版品' },
    garden: { en: 'UD’s Log', zh: 'UD’s Log' },
    about: { en: 'About', zh: '關於' },
    cv: { en: 'CV', zh: '履歷' },
  };
  const init = () => {
    const languageButton = document.querySelector('[data-udc-language-toggle]');
    const themeButton = document.querySelector('.udc-theme-toggle');
    const menuButton = document.querySelector('.udc-menu-toggle');
    const menu = document.querySelector('#udc-navigation');
    const updateLabels = () => {
      const zh = root.dataset.udcUiLang === 'zh';
      document.querySelectorAll('[data-udc-nav]').forEach(link => {
        const label = labels[link.dataset.udcNav];
        if (label) link.textContent = label[zh ? 'zh' : 'en'];
      });
      document.querySelectorAll('[data-udc-ui]').forEach(el => el.lang = zh ? 'zh-Hant' : 'en');
      if (document.querySelector('[data-udc-home]')) root.lang = zh ? 'zh-Hant' : 'en';
      languageButton?.setAttribute('aria-label', zh ? 'Switch interface to English' : '切換為中文介面');
      const dark = root.classList.contains('dark');
      themeButton?.setAttribute('aria-label', zh ? (dark ? '切換為淺色模式' : '切換為深色模式') : (dark ? 'Switch to light mode' : 'Switch to dark mode'));
      themeButton?.setAttribute('aria-pressed', String(dark));
      const expanded = menuButton?.getAttribute('aria-expanded') === 'true';
      menuButton?.setAttribute('aria-label', zh ? (expanded ? '關閉選單' : '開啟選單') : (expanded ? 'Close menu' : 'Open menu'));
    };
    languageButton?.addEventListener('click', () => {
      root.dataset.udcUiLang = root.dataset.udcUiLang === 'zh' ? 'en' : 'zh';
      try { localStorage.setItem('udc-ui-language', root.dataset.udcUiLang); } catch (_) {}
      updateLabels();
    });
    const closeMenu = () => {
      menuButton?.setAttribute('aria-expanded', 'false');
      menu?.classList.remove('is-open');
      updateLabels();
    };
    menuButton?.addEventListener('click', () => {
      const open = menuButton.getAttribute('aria-expanded') !== 'true';
      menuButton.setAttribute('aria-expanded', String(open));
      menu.classList.toggle('is-open', open);
      updateLabels();
    });
    menu?.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && menuButton?.getAttribute('aria-expanded') === 'true') {
        closeMenu();
        menuButton.focus();
      }
    });
    document.addEventListener('click', event => {
      if (!event.target.closest('.udc-nav')) closeMenu();
    });
    matchMedia('(min-width: 821px)').addEventListener('change', closeMenu);
    new MutationObserver(updateLabels).observe(root, { attributes: true, attributeFilter: ['class'] });
    updateLabels();
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
