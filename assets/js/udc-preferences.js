// Apply the UI language before paint; original article languages remain intact.
(() => {
  let saved;
  try { saved = localStorage.getItem('udc-ui-language'); } catch (_) {}
  document.documentElement.dataset.udcUiLang = ['en', 'zh'].includes(saved)
    ? saved : navigator.language.toLowerCase().startsWith('zh') ? 'zh' : 'en';
})();
