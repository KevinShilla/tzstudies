/* Shared navigation, combined library filters, and the study assistant. */
(function () {
  'use strict';
  const toggle = document.querySelector('.nav-toggle');
  const menu = document.getElementById('navMenu');
  function closeMenu() {
    if (!toggle || !menu) return;
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'Open navigation');
    menu.classList.remove('nav-open');
  }
  if (toggle && menu) {
    toggle.addEventListener('click', function () {
      const open = toggle.getAttribute('aria-expanded') !== 'true';
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
      menu.classList.toggle('nav-open', open);
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && menu.classList.contains('nav-open')) {
        closeMenu();
        toggle.focus();
      }
    });
    document.addEventListener('click', function (event) {
      if (!event.target.closest('.navbar')) closeMenu();
    });
    menu.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
  }

  const search = document.getElementById('searchInput');
  const subject = document.getElementById('subjectFilter');
  const year = document.getElementById('yearFilter');
  const cards = Array.from(document.querySelectorAll('#examGrid .exam-card'));
  const gradeButtons = Array.from(document.querySelectorAll('.grade-btn'));
  const count = document.getElementById('resultCount');
  const empty = document.getElementById('noResults');
  let grade = '';
  function filterPapers() {
    const terms = (search ? search.value.toLowerCase().trim() : '').split(/\s+/).filter(Boolean);
    let visible = 0;
    cards.forEach(card => {
      const show = (!grade || card.dataset.grade === grade)
        && (!subject || !subject.value || card.dataset.subject === subject.value)
        && (!year || !year.value || card.dataset.year === year.value)
        && terms.every(term => /^\d+$/.test(term)
          ? card.dataset.search.split(/\W+/).includes(term)
          : card.dataset.search.includes(term));
      card.hidden = !show;
      if (show) visible++;
    });
    if (count) count.textContent = visible + (visible === 1 ? ' paper' : ' papers');
    if (empty) empty.hidden = visible !== 0;
  }
  [search, subject, year].filter(Boolean).forEach(el => el.addEventListener(el === search ? 'input' : 'change', filterPapers));
  gradeButtons.forEach(button => button.addEventListener('click', () => {
    grade = button.dataset.grade;
    gradeButtons.forEach(b => {
      b.classList.toggle('active', b === button);
      b.setAttribute('aria-pressed', String(b === button));
    });
    filterPapers();
  }));
  const clear = document.getElementById('clearFilters');
  if (clear) clear.addEventListener('click', () => {
    [search, subject, year].filter(Boolean).forEach(el => { el.value = ''; });
    grade = '';
    gradeButtons.forEach(b => {
      b.classList.toggle('active', b.dataset.grade === '');
      b.setAttribute('aria-pressed', String(b.dataset.grade === ''));
    });
    filterPapers();
    search.focus();
  });

  const aiForm = document.getElementById('aiForm');
  const aiQuery = document.getElementById('aiQuery');
  const askButton = document.getElementById('askButton');
  const aiResponse = document.getElementById('aiResponse');
  if (aiForm && aiQuery && askButton && aiResponse) {
    aiForm.addEventListener('submit', async function (event) {
      event.preventDefault();
      const query = aiQuery.value.trim();
      if (!query || askButton.disabled) return;
      aiResponse.hidden = false;
      aiResponse.textContent = 'Working through your question...';
      aiResponse.setAttribute('aria-busy', 'true');
      askButton.disabled = true;
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 45000);
      try {
        const response = await fetch('/ask', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content },
          body: JSON.stringify({ query }),
          signal: controller.signal
        });
        const data = await response.json();
        aiResponse.textContent = data.answer || data.error || 'Please try again in a moment.';
      } catch (error) {
        aiResponse.textContent = error.name === 'AbortError'
          ? 'This is taking longer than expected. Please try again.'
          : 'We could not connect. Check your connection and try again.';
      } finally {
        clearTimeout(timeout);
        askButton.disabled = false;
        aiResponse.setAttribute('aria-busy', 'false');
      }
    });
  }
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('/sw.js').catch(() => {});
    });
  }
})();
