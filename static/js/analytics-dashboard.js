/* Private dashboard, native SVG charts and safe text rendering; no external analytics SDK. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const count = value => new Intl.NumberFormat('en').format(value || 0);
  const amount = (value, word) => `${count(value)} ${word}${value === 1 ? '' : 's'}`;
  const duration = value => value > 0 && value < 1 ? '<1s' : value < 60 ? `${Math.round(value)}s` : `${Math.floor(value / 60)}m ${Math.round(value % 60)}s`;
  const names = { page_view: 'Page viewed', signup_start: 'Started signup', signup_complete: 'Completed signup',
    signup_leave: 'Left signup', login: 'Logged in', button_click: 'Button clicked', search: 'Searched the library', feature_use: 'Used a feature' };
  let data, period = '30d', metric = 'visitors', pageLimit = 15, sourceLimit = 8, requestNumber = 0, controller, pendingCustom = false;
  const params = new URLSearchParams(location.search);
  if (['today', '7d', '30d', 'month', 'all', 'custom'].includes(params.get('period'))) period = params.get('period');
  $('analyticsStart').value = params.get('start') || '';
  $('analyticsEnd').value = params.get('end') || '';
  $('comparePeriod').checked = params.get('compare') !== '0';
  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }
  function empty(target, text = 'No activity recorded for these dates yet.') {
    target.replaceChildren(el('p', 'analytics-empty', text));
  }
  function selectPeriod() {
    document.querySelectorAll('[data-period]').forEach(button => {
      const selected = button.dataset.period === period;
      button.classList.toggle('selected', selected); button.setAttribute('aria-pressed', String(selected));
    });
    $('customDates').hidden = period !== 'custom';
    $('analyticsStart').disabled = $('analyticsEnd').disabled = period !== 'custom';
    $('comparePeriod').disabled = period === 'all';
  }
  async function load({ background = false } = {}) {
    if (pendingCustom && background) return;
    controller?.abort(); controller = new AbortController();
    const number = ++requestNumber;
    const query = new URLSearchParams({ period, compare: $('comparePeriod').checked ? '1' : '0' });
    if (period === 'custom') { query.set('start', $('analyticsStart').value); query.set('end', $('analyticsEnd').value); }
    $('analyticsContent').setAttribute('aria-busy', 'true');
    $('analyticsRefresh').disabled = true;
    const timeout = setTimeout(() => controller.abort(), 15000);
    try {
      const response = await fetch('/admin/analytics/data?' + query, { credentials: 'same-origin', signal: controller.signal, cache: 'no-store' });
      if (response.redirected || response.status === 403) throw new Error('Your admin session has expired. Log in again to view analytics.');
      if (!response.headers.get('content-type')?.includes('application/json')) throw new Error('Analytics could not load. Please refresh in a moment.');
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'Analytics could not load. Please refresh in a moment.');
      if (number !== requestNumber) return;
      data = result; pendingCustom = false; $('analyticsError').hidden = true;
      if (period !== 'custom') { $('analyticsStart').value = data.range.start; $('analyticsEnd').value = data.range.end; }
      $('analyticsStart').max = $('analyticsEnd').max = data.range.today;
      history.replaceState(null, '', location.pathname + '?' + query);
      render();
    } catch (error) {
      if (number === requestNumber) {
        $('analyticsError').textContent = error.name === 'AbortError' ? 'Analytics took too long to load. Try Refresh.' : error.message;
        $('analyticsError').hidden = false;
      }
    } finally {
      clearTimeout(timeout);
      if (number === requestNumber) { $('analyticsContent').setAttribute('aria-busy', 'false'); $('analyticsRefresh').disabled = false; }
    }
  }
  function delta(key) {
    const node = $('change-' + key), change = data.comparison?.[key];
    node.className = 'analytics-delta';
    if (!change) { node.textContent = 'Selected period'; return; }
    node.classList.add(change.direction);
    if (change.change === null) node.textContent = change.current ? 'New activity · previous period 0' : 'No activity in either period';
    else if (change.direction === 'flat') node.textContent = 'No change vs previous period';
    else node.textContent = `${change.direction === 'up' ? '↑' : '↓'} ${Math.abs(change.change)}${change.unit} vs previous period`;
    node.title = `Previous period: ${change.previous}${key === 'conversion' ? '%' : ''}`;
  }
  function render() {
    const { summary: s, range, totals } = data;
    ['visitors', 'views', 'signups', 'conversion'].forEach(key => { $('stat-' + key).textContent = key === 'conversion' ? s.conversion.toFixed(1) + '%' : count(s[key]); delta(key); });
    $('detail-visitors').textContent = `${count(s.visits)} total visit${s.visits === 1 ? '' : 's'} · anonymous browsers`;
    $('detail-views').textContent = `${duration(s.average_time)} average active time per page`;
    $('detail-signups').textContent = 'Successful accounts · excludes the admin';
    $('detail-conversion').textContent = 'Recorded visitors who completed signup';
    $('periodCaption').textContent = `${range.start} — ${range.end} · updated ${new Intl.DateTimeFormat('en-GB', { timeZone: 'Africa/Dar_es_Salaam', hour: '2-digit', minute: '2-digit' }).format(new Date())}`;
    ['today', 'week', 'month'].forEach(key => { $('calendar-' + key).textContent = `${amount(data.calendar[key].visitors, 'visitor')} · ${amount(data.calendar[key].signups, 'signup')}`; });
    $('calendar-all').textContent = `${amount(totals.visitors, 'visitor')} · ${amount(totals.visits, 'visit')} · ${amount(totals.views, 'view')} · ${amount(totals.signups, 'signup')}`;
    $('trendTotal').textContent = `${amount(s.visits, 'visit')} in this period`;
    const change = data.comparison?.engagement_rate;
    $('engagementMetric').textContent = `${s.engagement_rate.toFixed(1)}% engaged visits${change && change.direction !== 'flat' ? ` · ${change.change > 0 ? '+' : ''}${change.change}pp` : ''}`;
    $('audienceTotal').textContent = count(s.visitors);
    const newPercent = s.visitors ? 100 * s.new_visitors / s.visitors : 0;
    $('audienceDonut').style.background = s.visitors ? `conic-gradient(#377b5c 0 ${newPercent}%, #d0dc9e ${newPercent}% 100%)` : '#eef3e9';
    $('audienceLegend').replaceChildren();
    for (const [label, value, returning] of [['New visitors', s.new_visitors, false], ['Returning visitors', s.returning_visitors, true]]) {
      const item = el('div'); const caption = el('p'); caption.append(el('span', 'analytics-legend-dot' + (returning ? ' returning' : '')), document.createTextNode(label));
      item.append(caption, el('strong', '', count(value)), el('p', '', `${s.visitors ? Math.round(100 * value / s.visitors) : 0}% of visitors`)); $('audienceLegend').append(item);
    }
    renderCharts(); renderSources(); renderPages(); renderFunnel();
    ranking('entryRows', data.entries.slice(0, 7), 'visits');
    ranking('exitRows', data.exits.slice(0, 7), 'visits', 'No completed visits yet. Active visits can continue.');
    $('signupTotal').textContent = `${count(s.signups)} total signup${s.signups === 1 ? '' : 's'}`;
    $('signupMetrics').replaceChildren();
    for (const [label, value] of [['Started visits', s.signup_starts], ['Completed accounts', s.tracked_signups], ['Left / timed out', s.signup_abandoned]]) {
      const box = el('div'); box.append(el('strong', '', count(value)), el('span', '', label)); $('signupMetrics').append(box);
    }
    $('signupHistoryNote').textContent = data.unattributed_signups ? `${count(data.unattributed_signups)} signup(s) have no traffic attribution: created before tracking or while tracking was unavailable or opted out.` : 'Only the server can confirm signup completion. Leaving the form counts as abandonment only if that visit never completes signup.';
    const combinedSources = new Map();
    data.sources.forEach(row => { combinedSources.set(row.source, (combinedSources.get(row.source) || 0) + row.signups); });
    ranking('signupSourceRows', Array.from(combinedSources, ([title, signups]) => ({ title, signups })).filter(row => row.signups).sort((a,b) => b.signups - a.signups).slice(0, 5), 'signups', 'No attributed signups for these dates.');
    ranking('signupPageRows', data.signup_pages.slice(0, 5), 'signups', 'No attributed signups for these dates.');
    renderJourneys(); renderRecent();
    ranking('eventRows', data.event_counts.map(row => ({ title: names[row.name] || row.name, path: row.label.replaceAll('_', ' '), count: row.count })), 'count');
    $('trackingNote').textContent = data.tracking_since ? `Traffic recording began ${new Intl.DateTimeFormat('en-GB', { timeZone: 'Africa/Dar_es_Salaam', dateStyle: 'medium' }).format(new Date(data.tracking_since))}. Earlier visitor history cannot be recovered. Signup totals include existing accounts.` : 'No visits recorded yet. Traffic recording begins with public website visits; your admin browsing is excluded. Existing signup totals are still available.';
  }
  function chart(target, key, small = false) {
    const points = data.trend.points, width = Math.max(300, target.clientWidth), height = small ? 165 : 215;
    const left = 32, right = width - 10, top = 16, bottom = height - 28;
    const values = points.map(point => point[key]);
    const max = Math.max(4, Math.ceil(Math.max(...values, 0) / 4) * 4);
    const ns = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(ns, 'svg'); svg.setAttribute('viewBox', `0 0 ${width} ${height}`); svg.setAttribute('role', 'img');
    const label = `${key === 'views' ? 'Page views' : key === 'signups' ? 'Signups' : 'Unique visitors'} by ${data.trend.interval}`;
    svg.setAttribute('aria-label', label);
    function add(tag, attrs, text, parent = svg) {
      const node = document.createElementNS(ns, tag);
      Object.entries(attrs).forEach(([name, value]) => node.setAttribute(name, value));
      if (text !== undefined) node.textContent = text;
      parent.append(node); return node;
    }
    const gradientId = `chart-fill-${key}`;
    const defs = add('defs', {}); const gradient = add('linearGradient', { id: gradientId, x1: 0, y1: 0, x2: 0, y2: 1 }, undefined, defs);
    add('stop', { offset: '0%', 'stop-color': '#92bc73', 'stop-opacity': '.35' }, undefined, gradient);
    add('stop', { offset: '100%', 'stop-color': '#dcecca', 'stop-opacity': '.1' }, undefined, gradient);
    for (let index = 0; index <= 4; index++) {
      const y = bottom - index * (bottom - top) / 4;
      add('line', { x1: left, y1: y, x2: right, y2: y, stroke: '#eaf0e2', 'stroke-dasharray': index ? '3 4' : 'none' });
      add('text', { x: left - 8, y: y + 3, 'text-anchor': 'end' }, count(max * index / 4));
    }
    const coords = values.map((value, index) => [points.length === 1 ? (left + right) / 2 : left + index * (right - left) / (points.length - 1), bottom - value * (bottom - top) / max]);
    if (coords.length) {
      const line = coords.map(([x, y], index) => `${index ? 'L' : 'M'}${x.toFixed(1)},${y.toFixed(1)}`).join(' ');
      add('path', { d: `${line} L${coords.at(-1)[0]},${bottom} L${coords[0][0]},${bottom} Z`, fill: `url(#${gradientId})` });
      add('path', { d: line, fill: 'none', stroke: '#43825c', 'stroke-width': 2.5, 'stroke-linejoin': 'round', 'stroke-linecap': 'round' });
      coords.forEach(([x,y], index) => {
        const title = `${points[index].date}: ${count(values[index])} ${key}`;
        const circle = add('circle', { cx: x, cy: y, r: points.length < 35 ? 3 : 2, fill: '#43825c', class: 'chart-point', tabindex: index % Math.max(1, Math.floor(points.length / 10)) === 0 ? 0 : -1, 'aria-label': title });
        add('title', {}, title, circle);
        if (!small) { circle.addEventListener('mouseenter', () => { $('trendCaption').textContent = title; }); circle.addEventListener('focus', () => { $('trendCaption').textContent = title; }); }
      });
      const positions = [...new Set([0, Math.floor((points.length - 1) / 2), points.length - 1])];
      positions.forEach(index => { add('text', { x: coords[index][0], y: height - 8, 'text-anchor': index === 0 ? 'start' : index === points.length - 1 ? 'end' : 'middle' }, points[index].date); });
      if (!values.some(Boolean)) add('text', { x: (left + right) / 2, y: (top + bottom) / 2, 'text-anchor': 'middle' }, 'No activity for these dates');
    }
    target.replaceChildren(svg);
  }
  function renderCharts() {
    if (!data) return;
    $('trendCaption').textContent = `${metric === 'visitors' ? 'Unique visitors' : 'Page views'} per ${data.trend.interval}. Hover or focus a point for details.`;
    chart($('visitorChart'), metric); chart($('signupChart'), 'signups', true);
  }
  function renderSources() {
    const rows = data.sources.filter(row => $('sourceChannel').value === 'all' || row.channel === $('sourceChannel').value);
    const target = $('sourceRows'); target.replaceChildren();
    if (!rows.length) { empty(target, 'No traffic from this source for these dates.'); $('showSources').hidden = true; return; }
    const max = Math.max(...rows.map(row => row.visitors), 1);
    rows.slice(0, sourceLimit).forEach(row => {
      const box = el('div', 'analytics-source-row'), header = el('div', 'analytics-source-header'), title = el('div');
      title.append(el('strong', '', row.source), el('small', '', [row.channel, row.referrer].filter(Boolean).join(' · ')));
      const number = el('span', '', amount(row.visitors, 'visitor')); number.append(el('small', '', amount(row.signups, 'signup')));
      header.append(title, number); const bar = el('div', 'analytics-bar'), fill = el('span'); fill.style.width = `${100 * row.visitors / max}%`; bar.append(fill); box.append(header, bar); target.append(box);
    });
    $('showSources').hidden = rows.length <= sourceLimit;
  }
  function renderFunnel() {
    const target = $('signupFunnel'); target.replaceChildren();
    data.funnel.forEach((step, index) => {
      if (index) target.append(el('div', 'analytics-funnel-arrow', `↓ ${step.dropoff}% drop-off`));
      const box = el('div', 'analytics-funnel-step'), line = el('div', 'analytics-funnel-line');
      line.append(el('span', '', `${index + 1}. ${step.label}`), el('strong', '', count(step.count)));
      const bar = el('div', 'analytics-bar'), fill = el('span'); fill.style.width = `${step.progress}%`; bar.append(fill);
      box.append(line, bar, el('small', '', `${step.progress}% of recorded visitors`)); target.append(box);
    });
  }
  function renderPages() {
    const query = $('pageFilter').value.toLowerCase().trim();
    const rows = data.pages.filter(row => (row.title + ' ' + row.path).toLowerCase().includes(query));
    const sort = $('pageSort').value;
    rows.sort((a,b) => sort === 'least' ? a.views - b.views || a.path.localeCompare(b.path) : sort === 'time' ? b.average_time - a.average_time : sort === 'exit' ? b.exit_rate - a.exit_rate : b.views - a.views || a.path.localeCompare(b.path));
    const target = $('pageRows'); target.replaceChildren();
    rows.slice(0, pageLimit).forEach(row => {
      const tr = el('tr'), title = el('td'); title.append(el('strong', '', row.title), el('small', '', row.path)); tr.append(title);
      [count(row.views), count(row.visitors), row.timed_views ? duration(row.average_time) : '—', row.views ? `${row.exit_rate}%` : '—'].forEach(value => tr.append(el('td', '', value))); target.append(tr);
    });
    if (!rows.length) { const tr = el('tr'), td = el('td', '', 'No matching pages.'); td.colSpan = 5; tr.append(td); target.append(tr); }
    $('pagesCaption').textContent = `Showing ${Math.min(pageLimit, rows.length)} of ${rows.length} pages`;
    $('showPages').hidden = rows.length <= pageLimit;
  }
  function ranking(id, rows, value, message) {
    const target = $(id); target.replaceChildren();
    if (!rows.length) { empty(target, message); return; }
    rows.forEach(row => {
      const box = el('div', 'analytics-ranking-row'), title = el('div'); title.append(el('strong', '', row.title || row.path));
      if (row.path) title.append(el('small', '', row.path)); box.append(title, el('span', '', count(row[value]))); target.append(box);
    });
  }
  function renderJourneys() {
    const target = $('journeyRows'); target.replaceChildren();
    $('journeyCaption').textContent = `${data.journeys_sample} recent visits sampled`;
    if (!data.journeys.length) empty(target, 'Visitor paths will appear as people browse the website.');
    data.journeys.forEach(journey => {
      const row = el('div', 'analytics-journey'), path = el('div', 'analytics-path');
      journey.pages.forEach((page, index) => { if (index) path.append(el('i', '', '→')); const node = el('span', '', page.title); node.title = page.path; path.append(node); });
      row.append(path, el('strong', '', `${count(journey.visits)} visit${journey.visits === 1 ? '' : 's'}`)); target.append(row);
    });
    ranking('transitionRows', data.transitions.map(row => ({ title: `${row.from_title} → ${row.to_title}`, visits: row.visits })), 'visits', 'No multi-page journeys recorded for these dates yet.');
  }
  function renderRecent() {
    const target = $('recentRows'); target.replaceChildren();
    if (!data.recent.length) { empty(target); return; }
    data.recent.forEach(row => {
      const box = el('div', 'analytics-recent-row'), detail = el('div');
      detail.append(el('strong', '', names[row.event] || row.event), el('small', '', `${row.label.replaceAll('_', ' ')} · ${row.source}`), el('small', '', row.path));
      const time = el('time', '', new Intl.DateTimeFormat('en-GB', { timeZone: 'Africa/Dar_es_Salaam', hour: '2-digit', minute: '2-digit' }).format(new Date(row.at)));
      time.dateTime = row.at; time.title = new Intl.DateTimeFormat('en-GB', { timeZone: 'Africa/Dar_es_Salaam', dateStyle: 'medium', timeStyle: 'short' }).format(new Date(row.at));
      box.append(detail, time); target.append(box);
    });
  }
  document.querySelectorAll('[data-period]').forEach(button => button.addEventListener('click', () => {
    period = button.dataset.period; selectPeriod(); pageLimit = 15; sourceLimit = 8;
    if (period === 'custom') { pendingCustom = true; $('periodCaption').textContent = 'Choose dates and press Apply dates to update these reports.'; }
    else { pendingCustom = false; load(); }
  }));
  $('analyticsFilters').addEventListener('submit', event => { event.preventDefault(); if (period === 'custom') { pendingCustom = false; load(); } });
  $('comparePeriod').addEventListener('change', () => { if (!pendingCustom) load(); });
  $('analyticsRefresh').addEventListener('click', () => { if (!pendingCustom) load(); });
  $('pageFilter').addEventListener('input', () => { if (data) { pageLimit = 15; renderPages(); } });
  $('pageSort').addEventListener('change', () => { if (data) { pageLimit = 15; renderPages(); } });
  $('sourceChannel').addEventListener('change', () => { if (data) { sourceLimit = 8; renderSources(); } });
  $('showPages').addEventListener('click', () => { pageLimit += 30; renderPages(); });
  $('showSources').addEventListener('click', () => { sourceLimit = 200; renderSources(); });
  document.querySelectorAll('[data-metric]').forEach(button => button.addEventListener('click', () => {
    metric = button.dataset.metric;
    document.querySelectorAll('[data-metric]').forEach(item => { item.classList.toggle('selected', item === button); item.setAttribute('aria-pressed', String(item === button)); }); renderCharts();
  }));
  let resizeTimer; window.addEventListener('resize', () => { clearTimeout(resizeTimer); resizeTimer = setTimeout(renderCharts, 150); });
  setInterval(() => { if (document.visibilityState === 'visible') load({ background: true }); }, 60000);
  selectPeriod(); load();
})();
