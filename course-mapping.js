document.getElementById('course-form').addEventListener('submit', function(event) {
  event.preventDefault(); // Prevent form submission

  // Display a pop-up message
 alert('Details have been saved successfully!');

  // Optionally, you can reset the form after saving
  this.reset();
});
