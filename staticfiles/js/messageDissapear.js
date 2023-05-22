document.addEventListener('DOMContentLoaded', function() {
    // Get all Django messages elements
    var messages = document.getElementsByClassName('messages');
  
    // Loop through each message element
    Array.from(messages).forEach(function(message) {
      // Hide the message after 3 seconds
      setTimeout(function() {
        message.style.display = 'none';
      }, 3000);
    });
  });