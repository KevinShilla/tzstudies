<<<<<<< HEAD
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
=======
document.getElementById('searchInput').addEventListener('input', function() {
    const filter = this.value.toLowerCase();
    const cards = document.querySelectorAll('.exam-card');
  
    cards.forEach(card => {
      const text = card.textContent.toLowerCase();
      card.style.display = text.includes(filter) ? '' : 'none';
    });
});


document.getElementById('askButton').addEventListener('click', function() {
    let query = document.getElementById('aiQuery').value;
    let responseDiv = document.getElementById('aiResponse');
    responseDiv.textContent = "Loading answer...";

    fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query })
    })
    .then(response => response.json())
    .then(data => {
        if (data.answer) {
            responseDiv.textContent = data.answer;
        } else if (data.error) {
            responseDiv.textContent = "Error: " + data.error;
        }
    })
    .catch(error => {
        responseDiv.textContent = "Error: " + error;
    });
});
>>>>>>> b0f630e630adb5cf1db102ce373ade117d49b2ab
