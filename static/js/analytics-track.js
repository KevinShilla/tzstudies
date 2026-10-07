/* Anonymous first-party analytics. Never read names, emails, passwords or search text. */
(() => {
  'use strict';
  const ticket = document.querySelector('meta[name="analytics-ticket"]')?.content;
  const csrf = document.querySelector('meta[name="csrf-token"]')?.content;
  if (!ticket || !csrf || navigator.doNotTrack === '1' || navigator.globalPrivacyControl) return;
  const endpoint = '/analytics/collect';
  let activeMs = 0, since = document.visibilityState === 'visible' ? performance.now() : null;
  let queue = [], sequence = 0, occurrence = '', signupStarted = false, submitting = false, timer;
  const newId = () => {
    const bytes = new Uint8Array(8);
    crypto.getRandomValues(bytes);
    return Array.from(bytes, byte => byte.toString(16).padStart(2, '0')).join('');
  };
  function time() {
    const now = performance.now();
    if (since !== null) { activeMs += now - since; since = now; }
    return Math.min(14400, Math.floor(activeMs / 1000));
  }
  function flush(state = 'active', beacon = false) {
    clearTimeout(timer);
    const events = queue.splice(0, 12);
    const payload = JSON.stringify({ ticket, seconds: time(), state, sequence: sequence++, occurrence, events });
    // FormData carries CSRF protection even when sendBeacon cannot set request headers.
    const body = new FormData();
    body.append('csrf_token', csrf); body.append('payload', payload);
    if (beacon && navigator.sendBeacon?.(endpoint, body)) return;
    fetch(endpoint, { method: 'POST', body, credentials: 'same-origin', keepalive: true })
      .then(response => { if (!response.ok && state === 'active') queue = events.concat(queue).slice(0, 12); })
      .catch(() => { if (state === 'active') queue = events.concat(queue).slice(0, 12); });
  }
  function track(name, label) {
    if (queue.length < 12) queue.push({ id: newId(), name, label });
    clearTimeout(timer); timer = setTimeout(() => flush(), 200);
  }
  // Page creation is idempotent by signed page ticket; retries cannot inflate views.
  flush();
  setInterval(() => { if (document.visibilityState === 'visible') flush(); }, 30000);
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') {
      time(); since = null; if (!submitting) flush('hidden', true);
    } else { since = performance.now(); flush('active'); }
  });
  window.addEventListener('pagehide', () => {
    if (submitting) return;
    if (signupStarted && !submitting) track('signup_leave', 'signup_form');
    flush('ended', true);
  });
  window.addEventListener('pageshow', event => {
    if (event.persisted) { occurrence = newId(); activeMs = 0; sequence = 0; submitting = false; since = performance.now(); flush('active'); }
  });
  const signup = location.pathname === '/signup' ? document.querySelector('.auth-form') : null;
  const startSignup = () => {
    if (!signupStarted) { signupStarted = true; track('signup_start', 'signup_form'); }
  };
  if (signup) {
    signup.addEventListener('input', startSignup, { passive: true });
    signup.addEventListener('submit', () => { startSignup(); submitting = true; track('button_click', 'signup_submit'); flush('ended', true); });
  }
  const login = location.pathname === '/login' ? document.querySelector('.auth-form') : null;
  if (login) login.addEventListener('submit', () => { submitting = true; track('button_click', 'login'); flush('ended', true); });
  document.querySelectorAll('form[action="/logout"]').forEach(form => form.addEventListener('submit', () => { submitting = true; flush('ended', true); }));
  let searchTimer;
  document.querySelectorAll('input[type="search"]').forEach(input => {
    input.addEventListener('input', () => { clearTimeout(searchTimer); searchTimer = setTimeout(() => track('search', 'library_search'), 1200); });
  });
  document.querySelectorAll('.filter-selects select, #gradeFilter, #subjectFilter, #yearFilter').forEach(select => {
    select.addEventListener('change', () => track('feature_use', select.id === 'subjectSelect' ? 'tutor_filter' : 'library_filter'));
  });
  document.getElementById('aiForm')?.addEventListener('submit', () => track('feature_use', 'study_assistant'));
  document.addEventListener('click', event => {
    const el = event.target.closest('a, button');
    if (!el) return;
    let label;
    const href = el.getAttribute('href') || '';
    if (href.startsWith('tel:')) label = 'tutor_contact';
    else if (href.startsWith('/download_key/')) label = 'download_key';
    else if (href.startsWith('/download/')) label = 'download_exam';
    else if (href.startsWith('/view_key/')) label = 'open_key';
    else if (href.startsWith('/view/')) label = 'open_exam';
    else if (href.startsWith('/signup')) label = 'start_signup';
    else if (href.startsWith('/login')) label = 'login';
    else if (href === '/answer_keys') label = 'browse_keys';
    else if (href === '/tutors') label = 'find_tutors';
    else if (href === '#examSection' || href === '/#examSection') label = 'browse_papers';
    else if (el.matches('.grade-btn, #clearFilters, .standard-shortcut, .library-filter-actions .text-link')) label = 'library_filter';
    else if (el.matches('.reply-toggle')) label = 'discussion';
    else if (el.id === 'installBtn') label = 'install_app';
    else if (el.matches('.nav-link, .text-link, .btn') && href.startsWith('/')) label = 'navigation';
    if (label) track('button_click', label);
    // Record the final visible time before normal link navigation. Some browsers skip pagehide.
    if (el.tagName === 'A' && href && !event.defaultPrevented && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey
        && (!el.target || el.target === '_self') && !el.hasAttribute('download') && !href.startsWith('/download')) {
      const destination = new URL(href, location.href);
      const hashOnly = destination.pathname === location.pathname && destination.search === location.search && destination.hash;
      if (['http:', 'https:'].includes(destination.protocol) && !hashOnly) {
        if (signupStarted && !submitting) track('signup_leave', 'signup_form');
        flush('ended', true);
      }
    }
  }, { passive: true });
})();
