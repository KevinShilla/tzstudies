/* TZStudies — Main JavaScript */

(function() {
  'use strict';

  // --- Search Filtering (index page) ---
  var searchInput = document.getElementById('searchInput');
  if (searchInput) {
    searchInput.addEventListener('input', function() {
      var filter = this.value.toLowerCase();
      var cards = document.querySelectorAll('.exam-card');
      cards.forEach(function(card) {
        var text = card.textContent.toLowerCase();
        card.classList.toggle('hidden', !text.includes(filter));
      });
    });
  }

  // --- AI Study Assistant (index page) ---
  var askButton  = document.getElementById('askButton');
  var aiQuery    = document.getElementById('aiQuery');
  var aiResponse = document.getElementById('aiResponse');

  if (askButton && aiQuery && aiResponse) {
    askButton.addEventListener('click', function() {
      var query = aiQuery.value.trim();
      if (!query) return;

      aiResponse.textContent = 'Thinking...';
      askButton.disabled = true;

      fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query })
      })
      .then(function(res) { return res.json(); })
      .then(function(data) {
        if (data.answer) {
          aiResponse.textContent = data.answer;
        } else if (data.error) {
          aiResponse.textContent = 'Error: ' + data.error;
        }
      })
      .catch(function(err) {
        aiResponse.textContent = 'Error: ' + err.message;
      })
      .finally(function() {
        askButton.disabled = false;
      });
    });

    // Allow Enter key to submit
    aiQuery.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') { askButton.click(); }
    });
  }
})();
