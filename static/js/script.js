// Simple search filter for exam PDFs
document.getElementById('searchInput').addEventListener('input', function() {
    const filter = this.value.toLowerCase();
    // Select all .exam-card elements
    const cards = document.querySelectorAll('.exam-card');
  
    cards.forEach(card => {
      // Check the text content of each card
      const text = card.textContent.toLowerCase();
      // If it matches the filter, show it; otherwise, hide
      card.style.display = text.includes(filter) ? '' : 'none';
    });
});

// AI Assistant: Send query to the backend and display the response
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
