(() => {
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.nav-links');
  function closeMenu() { if (!toggle || !nav) return; nav.classList.remove('is-open'); toggle.setAttribute('aria-expanded', 'false'); }
  toggle?.addEventListener('click', () => { const open = nav.classList.toggle('is-open'); toggle.setAttribute('aria-expanded', String(open)); });
  nav?.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
  document.addEventListener('keydown', event => { if (event.key === 'Escape' && toggle?.getAttribute('aria-expanded') === 'true') { closeMenu(); toggle.focus(); } });
  const search = document.querySelector('#publication-search');
  const year = document.querySelector('#year-filter');
  const type = document.querySelector('#type-filter');
  const papers = [...document.querySelectorAll('[data-publication]')];
  function filter() {
    let count = 0;
    const query = search.value.trim().toLocaleLowerCase();
    papers.forEach(paper => {
      const visible = (!year.value || paper.dataset.year === year.value) && (!type.value || paper.dataset.type === type.value) && paper.dataset.search.includes(query);
      paper.hidden = !visible; if (visible) count++;
    });
    document.querySelector('#result-count').textContent = `${count} ${count === 1 ? 'publication' : 'publications'}`;
    document.querySelector('#no-results').hidden = count !== 0;
  }
  if (search) { search.addEventListener('input', filter); year.addEventListener('change', filter); type.addEventListener('change', filter); filter(); }
})();
