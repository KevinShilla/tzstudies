/* Reads stored status only. This page cannot confirm or initiate a payment. */
(() => {
  const state = document.getElementById('paymentState');
  if (!state) return;
  const terminal = ['paid', 'failed', 'refunded', 'reversed'];
  const messages = {
    paid: ['Payment confirmed', 'ClickPesa has confirmed your payment. Refresh to see the complete receipt.'],
    failed: ['Payment not completed', 'ClickPesa has not received this payment. You can check the status again before retrying.'],
    refunded: ['Payment refunded', 'ClickPesa reports that this payment has been refunded.'],
    reversed: ['Payment reversed', 'ClickPesa reports that this payment has been reversed.']
  };
  let remaining = 20;
  async function refresh() {
    if (document.hidden || remaining-- <= 0 || terminal.includes(state.dataset.status)) return;
    try {
      const result = await fetch(state.dataset.statusUrl, {credentials: 'same-origin', cache: 'no-store', headers: {Accept: 'application/json'}});
      if (!result.ok) return;
      const data = await result.json();
      state.dataset.status = data.status;
      document.getElementById('paymentStatus').textContent = data.status.replaceAll('_', ' ');
      if (messages[data.status]) {
        document.getElementById('paymentTitle').textContent = messages[data.status][0];
        document.getElementById('paymentMessage').textContent = messages[data.status][1];
        state.querySelector('.payment-symbol').textContent = data.status === 'paid' ? '✓' : '…';
        document.getElementById('pendingActions').hidden = data.status !== 'failed';
      }
    } catch (_) { /* Preserve the last verified status if offline. */ }
    if (!terminal.includes(state.dataset.status) && remaining > 0) setTimeout(refresh, 10000);
  }
  if (!terminal.includes(state.dataset.status)) setTimeout(refresh, 2000);
})();
