(() => {
  const storageKey = 'udc-ui-language';
  const root = document.documentElement;
  const navLabels = {
    research: { en: 'Research', zh: '研究' },
    publications: { en: 'Publications', zh: '出版品' },
    garden: { en: "UD's Log", zh: "UD's Log" },
    about: { en: 'About', zh: '關於' },
    cv: { en: 'CV', zh: '履歷' },
  };

  const getLanguage = () => {
    const saved = window.localStorage.getItem(storageKey);
    if (saved === 'en' || saved === 'zh') return saved;
    return navigator.language.toLowerCase().startsWith('zh') ? 'zh' : 'en';
  };

  const translateNavigation = (language) => {
    document.querySelectorAll('[data-udc-nav]').forEach((link) => {
      const label = navLabels[link.dataset.udcNav];
      if (label) link.textContent = label[language];
    });
  };

  const applyLanguage = (language) => {
    root.dataset.udcUiLang = language;
    root.lang = language === 'zh' ? 'zh-Hant' : 'en';
    window.localStorage.setItem(storageKey, language);
    const button = document.querySelector('[data-udc-language-toggle]');
    if (button) {
      button.setAttribute('aria-label', language === 'en' ? '切換為中文介面' : 'Switch interface to English');
      button.setAttribute('aria-pressed', language === 'zh' ? 'true' : 'false');
    }
    translateNavigation(language);
  };

  const tagNavigation = () => {
    const rules = [
      ['/#research', 'research'], ['/publication/', 'publications'],
      ['/post/', 'garden'], ['/experiences/', 'about'], ['/uploads/uei-dar-chen-cv.pdf', 'cv'],
    ];
    document.querySelectorAll('header a, nav a').forEach((link) => {
      const href = link.getAttribute('href') || '';
      const match = rules.find(([path]) => href === path || href.endsWith(path));
      if (match) link.dataset.udcNav = match[1];
    });
  };

  const createToggle = () => {
    if (document.querySelector('[data-udc-language-toggle]')) return;
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'udc-language-toggle';
    button.dataset.udcLanguageToggle = '';
    button.innerHTML = '<span class="udc-en">中文</span><span class="udc-zh">English</span>';
    button.addEventListener('click', () => {
      applyLanguage(root.dataset.udcUiLang === 'zh' ? 'en' : 'zh');
    });

    const themeButton = document.querySelector('.theme-toggle, button[aria-label*="theme" i], #theme-toggle, [data-theme-toggle]');
    if (themeButton?.parentElement) {
      themeButton.parentElement.insertBefore(button, themeButton);
      return;
    }
    const headerTools = document.querySelector('header nav > .order-1, header nav');
    if (headerTools) headerTools.appendChild(button);
  };

  const init = () => {
    tagNavigation();
    createToggle();
    applyLanguage(getLanguage());
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
