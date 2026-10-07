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

  // Filter the full catalogue on the server, rather than only the cards on this page.
  const libraryForm = document.querySelector('.library-filter-form');
  if (libraryForm) {
    libraryForm.querySelectorAll('select').forEach(select => {
      select.addEventListener('change', () => libraryForm.requestSubmit());
    });
  }

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
